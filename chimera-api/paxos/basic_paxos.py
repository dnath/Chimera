#
# basic_paxos.py -- basic paxos implementation
#

import pprint

import logging
FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


class InvalidDataError(Exception):
    pass

class Paxos:
    # Initialize Paxos instance
    def __init__(self, messenger):
        self.messenger = messenger
        # proposer fields
        self.proposal_number = [0, self.messenger.pid]
        self.proposal_value = 0
        # acceptor fields
        self.max_prepared = [-1, -1]
        self.max_accepted = [-1, -1]
        self.accepted_value = 0

    # implements the Paxos prepare message
    # if the prepare is accepted, return true and set the proposal_ fields
    # if the prepare is rejected, returns false
    def send_prepare(self, value):
        # set proposal fields
        self.proposal_number[0] = max(self.proposal_number[0]+1,
                self.max_prepared[0]+1) # guarantee this node will accept
        self.proposal_value = value
        logging.info("proposal_number = {0}".format(self.proposal_number))
        logging.info("proposal_value = {0}".format(self.proposal_value))

        # send prepare message to majority of nodes
        data = {}
        data['msg_type'] = 'prepare'
        data['proposal_number'] = self.proposal_number
        logging.info("data to be sent: \n{0}".format(pprint.pformat(data)))

        responses = self.messenger.broadcast_majority(data, '/paxos')
        # TODO check for empty dictionary -- no majority
        responses.update({self.messenger.pid : self.recv_prepare(data)})
        logging.info('responses = \n{0}'.format(pprint.pformat(responses)))


        # adopt value of largest accepted proposal number
        max_accepted = [-1, -1]
        for pid in iter(responses):
            data = responses[pid]

            # FIXME: check valid response
            if data['prepared'] == 'no':
                self.proposal_number[0] = data['max_prepared'][0]
                return False

            if data['prepared'] == 'yes' and data['max_accepted'] > max_accepted:
                max_accepted = list(data['max_accepted'])
                self.proposal_value = data['accepted_value'] 

        return True

    def recv_prepare(self, data):
        logging.info('received data: \n{0}'.format(pprint.pformat(data)))
        logging.info('proposal_number = {0}'.format(data['proposal_number']))
        logging.info('max_prepared = {0}'.format(self.max_prepared))
        if data['msg_type'] != 'prepare':
            raise InvalidDataError('received data = {0} is invalid!'.format(data))

        response = {}
        response['msg_type'] = 'prepare'
        if data['proposal_number'] > self.max_prepared:
            self.max_prepared = list(data['proposal_number'])
            response['prepared'] = 'yes'
            response['max_accepted'] = self.max_accepted
            response['accepted_value'] = self.accepted_value
        else:
            logging.info(type(self.max_prepared))
            response['prepared'] = 'no'
            response['max_prepared'] = self.max_prepared

        logging.info('response to be sent: \n{0}'.format(pprint.pformat(response)))
        return response

    # impements the Paxos accept message
    # if accept is accepted, return True and sets accepted_ fields
    # if accept is rejected, return False
    def send_accept(self):
        data = {}
        data['msg_type'] = 'accept'
        data['proposal_number'] = self.proposal_number
        data['value'] = self.proposal_value

        responses = self.messenger.broadcast_majority(data, '/paxos')
        responses.update({self.messenger.pid : self.recv_accept(data)})
        for pid in iter(responses):
            data = responses[pid]
            if data['accepted'] != 'yes':
                return False
        return True

    def recv_accept(self, data):
        response = {}
        response['msg_type'] = 'accept'
        if data['proposal_number'] >= self.max_prepared:
            response['accepted'] = 'yes'
            self.max_accepted = list(data['proposal_number'])
            self.accepted_value = data['value']
        else:
            response['accepted'] = 'no'
            response['max_prepared'] = self.max_prepared
        return response

