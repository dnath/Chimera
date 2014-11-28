#
# paxos.py -- paxos implementation
#

import json

class Paxos:
    # Initialize Paxos instance
    def __init__(self, msg, majority=1):
        self.msg = msg
        # proposer fields
        self.proposal_number = [0, self.msg.pid]
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
        self.proposal_number[0] += 1
        self.proposal_value = value
        # send prepare message to majority of nodes
        data = {}
        data['msg_type'] = 'prepare'
        data['proposal_number'] = self.proposal_number
        resp = self.msg.broadcast_majority(data, '/paxos')
        # adopt value of largest accepted proposal number
        max_accepted = [-1, -1]
        for key in iter(resp):
            data = resp[key]
            # FIXME: check valid response
            if data['prepared'] == 'no':
                self.proposal_number[0] = data['max_prepared'][0]
                return False
            if data['prepared'] == 'yes' and data['max_accepted'] > max_accepted: 
                max_accepted = data['max_accepted'][0]
                self.proposal_value = data['accepted_value'] 
        return True

    def recv_prepare(self, data):
        resp = {}
        resp['msg_type'] = 'prepare'
        if data['proposal_number'] > self.max_prepared:
            self.max_prepared = data['proposal_number']
            resp['prepared'] = 'yes'
            resp['max_accepted'] = self.max_accepted
            resp['accepted_value'] = self.accepted_value
        else:
            resp['prepared'] = 'no'
            resp['max_prepared'] = self.max_prepared
        return resp

    # impements the Paxos accept message
    # if accept is accepted, return True and sets accepted_ fields
    # if accept is rejected, return False
    def send_accept(self):
        data = {}
        data['msg_type'] = 'accept'
        data['proposal_number'] = self.proposal_number
        data['value'] = self.proposal_value
        resp = self.msg.broadcast_majority(data, '/paxos')
        for key in iter(resp):
            data = resp[key]
            if data['accepted'] != 'yes':
                return False
        return True

    def recv_accept(self, data):
        resp = {}
        resp['msg_type'] = 'accept'
        if data['proposal_number'] >= self.max_prepared:
            resp['accepted'] = 'yes'
            self.max_accepted = data['proposal_number']
            self.accepted_value = data['value']
        else:
            resp['accepted'] = 'no'
            resp['max_prepared'] = self.max_prepared
        return resp

