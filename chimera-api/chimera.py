#
# chimera.py -- top level event handlers
#

import json

from elect import Elect
from message import Message
from paxos import Paxos

class Chimera:
    def __init__(self, port):
        self.message = Message(port)
        self.paxos = Paxos(self.message)
        self.leader = None
        self.elect = Elect(self.message)
        self.elect.elect()

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

    def handle_prepare(self, value):
        return str(self.paxos.send_prepare(value))

    def handle_accept(self, value):
        return str(self.paxos.send_accept(value))

    def handle_elect(self, data):
        if data['msg_type'] == 'elect':
            resp = self.elect.recv_elect(data)
        if data['msg_type'] == 'leader':
            print '))) node %s chosen as new leader' % (data['pid'])
            resp = {}
            self.leader = int(data['pid'])
        resp['status'] = 'ok'
        return json.dumps(resp)

    def handle_leader(self):
        resp = {}
        resp['leader'] = self.leader
        resp['status'] = 'ok'
        return json.dumps(resp)

