#
# paxos.py -- paxos implementation
#

import json

class Paxos:
    # Initialize Paxos instance
    def __init__(self, message, majority=1):
        self.proposal_number = 0
        self.max_prepared = -1
        self.max_accepted = -1
        self.accepted_value = 0
        self.message = message

    def send_prepare(self, value):
        self.proposal_number += 1
        data = {}
        data['msg_type'] = 'prepare'
        data['proposal_number'] = str(self.proposal_number)
        
        resp = self.message.broadcast_majority(data, '/paxos')
        
        max_accepted = -1
        for key in iter(resp):
            data = resp[key]
            # FIXME: check valid response
            if data['prepared'] == 'no':
                print '))) prepare(%d) rejected by node %s' % (self.proposal_number, key)
                return '-1' #FIXME should be a better way to indicate failure
            if data['prepared'] == 'yes' and data['max_accepted'] > max_accepted: 
                max_accepted = data['max_accepted']
                value = data['accepted_value'] 
            print '))) prepare(%d) accepted by node %d, value set to %s' % (self.proposal_number, key, value)
        return value

    def recv_prepare(self, data):
        resp = {}
        resp['msg_type'] = 'prepare'
        if data['proposal_number'] > self.max_prepared:
            self.max_prepared = data['proposal_number']
            resp['prepared'] = 'yes'
            resp['max_accepted'] = self.max_accepted
            resp['accepted_value'] = self.accepted_value
            print '))) accepted prepare(%s) from node %s' % (self.max_prepared, data['pid'])
        else:
            resp['prepared'] = 'no'
            resp['max_prepared'] = self.max_prepared
            print '))) rejected prepare(%s) from node %s' % (self.max_prepared, data['pid'])
        return resp

    def send_accept(self, value):
        data = {}
        data['msg_type'] = 'accept'
        data['proposal_number'] = str(self.proposal_number)
        data['value'] = value
        resp = self.message.broadcast_majority(data, '/paxos')
        for key in iter(resp):
            data = resp[key]
            if data['accepted'] != 'yes':
                print '))) accept(%d) rejected by node %s' % (self.proposal_number, key)
                return -1
        print '))) value %s chosen' % (value)
        return value

    def recv_accept(self, data):
        resp = {}
        resp['msg_type'] = 'accept'
        # FIXME should this be >= ?
        if data['proposal_number'] >= self.max_prepared:
            resp['accepted'] = 'yes'
            self.max_accepted = data['proposal_number']
            self.accepted_value = data['value']
            print '))) accepted accept(%s) from node %s' % (self.max_prepared, data['pid'])
        else:
            resp['accepted'] = 'no'
            resp['max_prepared'] = self.max_prepared
            print '))) rejected accept(%s) from node %s' % (self.max_prepared, data['pid'])
        return resp

