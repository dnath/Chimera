#
# multi_paxos.py -- multi paxos implementation
#

import json
import pprint

import logging
FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


class InvalidDataError(Exception):
    pass

class Paxos:
    def __init__(self, messenger):
        self.paxos_instances = {}
        self.messenger = messenger

    def cleanup(self, paxos_index):
        if self.paxos_instances.has_key(paxos_index):
            self.paxos_instances.pop(paxos_index)

    def send_prepare(self, paxos_index, value):
        logging.info('index = {0}, value = {1}'.format(paxos_index, value))

        paxos_instance = self.__get_paxos_instance(paxos_index)

        paxos_instance.proposal_number[0] += 1
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
        logging.info('responses = \n{0}'.format(pprint.pformat(responses)))

        # adopt value of largest accepted proposal number
        max_accepted = [-1, -1]
        for pid in iter(responses):
            data = responses[pid]

            # FIXME: check valid response
            if data['prepared'] == 'no':
                paxos_instance.proposal_number[0] = data['max_prepared'][0]
                return False

            if data['prepared'] == 'yes' and data['max_accepted'] > max_accepted:
                max_accepted = data['max_accepted'][0]
                paxos_instance.proposal_value = data['accepted_value']

        return True

    def __get_paxos_instance(self, paxos_index):
        if not self.paxos_instances.has_key(paxos_index):
            self.paxos_instances[paxos_index] = BasicPaxos(pid=self.messenger.pid)

        return  self.paxos_instances[paxos_index]

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
            paxos_instance.max_prepared = data['proposal_number']
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
        paxos_instance = self.__get_paxos_instance(paxos_index)

        data = {}
        data['paxos_index'] = paxos_index
        data['msg_type'] = 'accept'
        data['proposal_number'] = paxos_instance.proposal_number
        data['value'] = paxos_instance.proposal_value

        responses = self.messenger.broadcast_majority(data, '/paxos')
        for pid in iter(responses):
            data = responses[pid]
            if data['accepted'] != 'yes':
                return False
        return True

    def recv_accept(self, data):
        paxos_index = data['paxos_index']
        paxos_instance = self.__get_paxos_instance(paxos_index)

        response = {}
        response['paxos_index'] = paxos_index
        response['msg_type'] = 'accept'
        if data['proposal_number'] >= paxos_instance.max_prepared:
            response['accepted'] = 'yes'
            paxos_instance.max_accepted = data['proposal_number']
            paxos_instance.accepted_value = data['value']
        else:
            response['accepted'] = 'no'
            response['max_prepared'] = paxos_instance.max_prepared

        return response

class BasicPaxos:
    # Initialize Paxos instance
    def __init__(self, pid):
        # proposer fields
        self.proposal_number = [0, pid]
        self.proposal_value = 0

        # acceptor fields
        self.max_prepared = [-1, -1]
        self.max_accepted = [-1, -1]
        self.accepted_value = 0