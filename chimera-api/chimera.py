#
# chimera.py -- top level event handlers
#

import json
import logging

FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

from elector import Elector
from messenger import Messenger
from paxos.basic_paxos import Paxos

class Chimera:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.messenger = Messenger(host=host, port=port)
        self.pid = self.messenger.pid

        self.paxos = Paxos(self.messenger)

        self.elector = Elector(self.messenger)
        self.leader_pid = self.elector.elect()
        self.leader = self.messenger.nodes[self.leader_pid]

        logging.info('Elected Leader: [%s] %s' % (self.leader_pid, self.leader))

    def is_leader(self):
        return self.pid == self.leader_pid

    def handle_withdraw(self, amount):
        response = {}
        if self.is_leader():
            # start paxos with first unchosen index
            pass
        else:
            response['status'] = 'forward'
            response['leader'] = self.leader

        return json.dumps(response)

    def handle_deposit(self, amount):
        response = {}
        if self.is_leader():
            # start paxos with first unchosen index
            pass
        else:
            response['status'] = 'forward'
            response['leader'] = self.leader

        return json.dumps(response)

    def handle_balance(self):
        response = {}
        if self.is_leader():
            # complete processing and return balance
            pass
        else:
            response['status'] = 'forward'
            response['leader'] = self.leader

        return json.dumps(response)

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
            response = self.elector.recv_elect(data)
            self.leader_pid = int(response['max_pid'])
            logging.info('Elected Leader: %s' % (self.messenger.nodes[self.leader_pid]))

        response['status'] = 'ok'

        return json.dumps(response)

    def handle_leader(self):
        response = {}
        response['leader'] = self.leader_pid
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




