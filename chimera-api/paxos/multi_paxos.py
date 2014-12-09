#
# multi_paxos.py -- multi paxos implementation
#

import json
import operator
import pickle
import pprint
from collections import Counter

import logging
FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


class InvalidDataError(Exception):
    pass

class Paxos:
    def __init__(self, messenger, filename='paxos.pickle'):
        self.messenger = messenger
        self.filename = filename
        try:
            self.paxos_instances = pickle.load(open(self.filename, 'r'))
        except:
            self.paxos_instances = {}

    def persist(self):
        pickle.dump(self.paxos_instances, open(self.filename, 'w'))

    def cleanup(self, paxos_index):
        if self.paxos_instances.has_key(paxos_index):
            self.paxos_instances.pop(paxos_index)

    def __select_value(self, paxos_instance, responses, result):
        is_value_changed = False
        max_accepted = [-1, -1]
        for pid in iter(responses):
            data = responses[pid]
            if data['prepared'] == 'no':
                logging.info('Server #{0} returned data["prepared""] == "no"'.format(pid))
                paxos_instance.proposal_number[0] = data['max_prepared'][0]
                result['return_code'] = False
                return result
            if data['prepared'] == 'yes' and data['max_accepted'] > max_accepted:
                max_accepted = list(data['max_accepted'])
                paxos_instance.proposal_value = data['accepted_value']
                is_value_changed = True
        result['is_value_changed'] = is_value_changed
        result['prepared_value'] = paxos_instance.proposal_value
        result['return_code'] = True
        return result

    def __select_value_enhanced(self, paxos_instance, responses, result):
        accepted_values = [list(resp['accepted_value']) for resp in responses.values()]
        vote_count = Counter(accepted_values)
        max_value = max(vote_count.iteritems(), key=operator.itemgetter(1))[0]
        max_votes = max(vote_count.iteritems(), key=operator.itemgetter(1))[1]
        if max_votes + len(responses) < self.messenger.majority:
            pass # generate combined value
        # TODO max_votes has majority
        else:
            return self.__select_value(paxos_instance, responses, result)

    # returns prepare_status, is_prepared_value_from_other_node
    def send_prepare(self, paxos_index, value):
        result = {'return_code': False,
                  'prepared_value': None,
                  'is_value_changed': False,
                  'got_majority': True}

        logging.info('index = {0}, value = {1}'.format(paxos_index, value))

        paxos_instance = self.__get_paxos_instance(paxos_index)

        # guarantee that we will accept our own proposal
        paxos_instance.proposal_number[0] = max(paxos_instance.proposal_number[0]+1, paxos_instance.max_prepared[0]+1)
        paxos_instance.proposal_value = value

        logging.info("proposal_number = {0}".format(paxos_instance.proposal_number))
        logging.info("proposal_value = {0}".format(paxos_instance.proposal_value))

        # send prepare message to majority of nodes
        data = {}
        data['paxos_index'] = paxos_index
        data['msg_type'] = 'prepare'
        data['proposal_number'] = paxos_instance.proposal_number
        logging.info("data to be sent: \n{0}".format(pprint.pformat(data)))

        responses = self.messenger.broadcast_majority(data, '/paxos')
        responses.update({self.messenger.pid : self.recv_prepare(data)})
        logging.info('responses = \n{0}'.format(pprint.pformat(responses)))

        if len(responses) < self.messenger.majority:
            result['got_majority'] = False
            logging.error('got_majority: {0}'.format(result['got_majority']))
            return result

        result = self.__select_value(paxos_instance, responses, result)
        self.persist()
        return result

    def __get_paxos_instance(self, paxos_index):
        if not self.paxos_instances.has_key(paxos_index):
            self.paxos_instances[paxos_index] = BasicPaxos(pid=self.messenger.pid)

        return self.paxos_instances[paxos_index]

    def recv_prepare(self, data):
        logging.info('received data: \n{0}'.format(pprint.pformat(data)))
        if data['msg_type'] != 'prepare' or not data.has_key('paxos_index'):
            raise InvalidDataError('received data is invalid!')

        paxos_index = data['paxos_index']
        logging.info('paxos_index = {0}'.format(paxos_index))

        paxos_instance = self.__get_paxos_instance(paxos_index)

        logging.info('max_prepared = {0}'.format(paxos_instance.max_prepared))

        response = {}
        response['paxos_index'] = paxos_index
        response['msg_type'] = 'prepare'
        if data['proposal_number'] > paxos_instance.max_prepared:
            paxos_instance.max_prepared = list(data['proposal_number'])
            self.persist()
            response['prepared'] = 'yes'
            response['max_accepted'] = paxos_instance.max_accepted
            response['accepted_value'] = paxos_instance.accepted_value

        else:
            response['prepared'] = 'no'
            response['max_prepared'] = paxos_instance.max_prepared

        logging.info('response to be sent: \n{0}'.format(pprint.pformat(response)))
        return response

    # impements the Paxos accept message
    # if accept is accepted, return True and sets accepted_ fields
    # if accept is rejected, return False
    def send_accept(self, paxos_index):
        response = {'return_code': True,
                    'got_majority': True}
        paxos_instance = self.__get_paxos_instance(paxos_index)

        data = {}
        data['paxos_index'] = paxos_index
        data['msg_type'] = 'accept'
        data['proposal_number'] = paxos_instance.proposal_number
        data['value'] = paxos_instance.proposal_value

        responses = self.messenger.broadcast_majority(data, '/paxos')
        responses.update({self.messenger.pid : self.recv_accept(data)})
        logging.info('responses = \n{0}'.format(pprint.pformat(responses)))

        if len(responses) < self.messenger.majority:
            response['got_majority'] = False
            response['return_code'] = False

            return False

        for pid in iter(responses):
            data = responses[pid]
            if data['accepted'] != 'yes':
                response['return_code'] = False
                return response

        return response

    def recv_accept(self, data):
        paxos_index = data['paxos_index']
        paxos_instance = self.__get_paxos_instance(paxos_index)

        response = {}
        response['paxos_index'] = paxos_index
        response['msg_type'] = 'accept'
        if data['proposal_number'] >= paxos_instance.max_prepared:
            response['accepted'] = 'yes'
            paxos_instance.max_accepted = list(data['proposal_number'])
            paxos_instance.accepted_value = data['value']
            self.persist()
        else:
            response['accepted'] = 'no'
            response['max_prepared'] = paxos_instance.max_prepared

        return response

class BasicPaxos:
    # Initialize Paxos instance
    def __init__(self, pid):
        # proposer fields
        self.proposal_number = [0, pid]
        self.proposal_value = None

        # acceptor fields
        self.max_prepared = [-1, -1]
        self.max_accepted = [-1, -1]
        self.accepted_value = 0
