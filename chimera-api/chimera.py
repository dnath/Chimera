#
# chimera.py -- top level event handlers
#

import json

import logging
FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

from elect import Elect
from messenger import Messenger
from paxos import Paxos

class Chimera:
    def __init__(self, port):
        self.messenger = Messenger(port)
        self.paxos = Paxos(self.messenger)
        self.elect = Elect(self.messenger)
        self.leader = self.elect.elect()
        logging.info('))) leader: %s' % (self.messenger.nodes[self.leader]))

    def handle_withdraw(self, amount):
        return 'ok'

    def handle_deposit(self, amount):
        return 'ok'

    def handle_balance(self):
        return 'ok'

    def handle_fail(self):
        return 'ok'

    def handle_unfail(self):
        return 'ok'

    def handle_paxos(self, data_json):
        response = {}

        if data_json['msg_type'] == 'prepare':
            response = self.paxos.recv_prepare(data_json)
        if data_json['msg_type'] == 'accept':
            response = self.paxos.recv_accept(data_json)

        response['status'] = 'ok'

        return json.dumps(response)

    def handle_elect(self, data):
        response = {}

        if data['msg_type'] == 'elect':
            response = self.elect.recv_elect(data)
            self.leader = int(response['max_pid'])
            logging.info('))) leader: %s' % (self.messenger.nodes[self.leader]))

        response['status'] = 'ok'

        return json.dumps(response)

    def handle_leader(self):
        response = {}
        response['leader'] = self.leader
        response['status'] = 'ok'
        return json.dumps(response)

    def handle_prepare(self, value):
        response = {}
        if self.paxos.send_prepare(int(value)):
            response['prepared'] = 'yes'
        else:
            response['prepared'] = 'no'

        response['proposal_value'] = self.paxos.proposal_value
        response['proposal_number'] = self.paxos.proposal_number
        #response['max_prepared'] = self.paxos.max_prepared
        #response['max_accepted'] = self.paxos.max_accepted
        #response['accepted_value'] = self.paxos.accepted_value
        response['status'] = 'ok'
        return json.dumps(response)

    def handle_chosen_value(self):
        response = {}
        response['chosen_value'] = self.paxos.proposal_value
        response['status'] = 'ok'
        return json.dumps(response)

    def handle_accept(self):
        response = {}
        if self.paxos.send_accept():
            response['accepted'] = 'yes'
        else:
            response['accepted'] = 'no'
        response['proposal_value'] = self.paxos.proposal_value
        response['proposal_number'] = self.paxos.proposal_number
        #response['max_prepared'] = self.paxos.max_prepared
        #response['max_accepted'] = self.paxos.max_accepted
        #response['accepted_value'] = self.paxos.accepted_value
        response['status'] = 'ok'
        return json.dumps(response)




