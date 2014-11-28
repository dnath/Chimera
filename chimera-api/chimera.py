#
# chimera.py -- top level event handlers
#

import json

from elect import Elect
from messenger import Messenger
from paxos import Paxos

class Chimera:
    def __init__(self, port):
        self.message = Messenger(port)
        self.paxos = Paxos(self.message)
        self.elect = Elect(self.message)
        self.leader = self.elect.elect()
        print '))) leader: %s' % (self.message.nodes[self.leader])

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

    def handle_paxos(self, data):
        #FIXME catch KeyError exception
        if data['msg_type'] == 'prepare':
            resp = self.paxos.recv_prepare(data)
        if data['msg_type'] == 'accept':
            resp = self.paxos.recv_accept(data)
        resp['status'] = 'ok'
        return json.dumps(resp)

    def handle_elect(self, data):
        if data['msg_type'] == 'elect':
            resp = self.elect.recv_elect(data)
            self.leader = int(resp['max_pid'])
            print '))) leader: %s' % (self.message.nodes[self.leader])
        resp['status'] = 'ok'
        return json.dumps(resp)

    def handle_leader(self):
        resp = {}
        resp['leader'] = self.leader
        resp['status'] = 'ok'
        return json.dumps(resp)

    def handle_prepare(self, value):
        resp = {}
        if self.paxos.send_prepare(int(value)):
            resp['prepared'] = 'yes'
        else:
            resp['prepared'] = 'no'
        resp['proposal_value'] = self.paxos.proposal_value
        resp['proposal_number'] = self.paxos.proposal_number
        #resp['max_prepared'] = self.paxos.max_prepared
        #resp['max_accepted'] = self.paxos.max_accepted
        #resp['accepted_value'] = self.paxos.accepted_value
        resp['status'] = 'ok'
        return json.dumps(resp)

    def handle_chosen_value(self):
        resp = {}
        resp['chosen_value'] = self.paxos.proposal_value
        resp['status'] = 'ok'
        return json.dumps(resp)

    def handle_accept(self):
        resp = {}
        if self.paxos.send_accept():
            resp['accepted'] = 'yes'
        else:
            resp['accepted'] = 'no'
        resp['proposal_value'] = self.paxos.proposal_value
        resp['proposal_number'] = self.paxos.proposal_number
        #resp['max_prepared'] = self.paxos.max_prepared
        #resp['max_accepted'] = self.paxos.max_accepted
        #resp['accepted_value'] = self.paxos.accepted_value
        resp['status'] = 'ok'
        return json.dumps(resp)




