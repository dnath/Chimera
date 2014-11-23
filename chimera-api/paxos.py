#
# paxos.py -- paxos implementation
#

import json
import urllib
import urllib2

class Paxos:
    # Send message to the next 'maj' nodes
    def __broadcast(self, data, maj=1):
        resp = {}
        for i in range(1, maj+1):
            print '))) send %s(%s) to node %d' % (data['msg_type'], data['proposal_number'], (self.pid + i) % 5)
            host = self.nodes[(self.pid + i) % 5]
            resp[i] = self.__msg_send(host, data)
        return resp

    # Send message 'data' to 'host'
    def __msg_send(self, host, data):
        url = 'http://' + host + '/paxos'
        encoded_data = urllib.urlencode(data)
        req = urllib2.Request(url, encoded_data)
        resp = urllib2.urlopen(req)
        return resp.read()

    # Retrieve node configuration from god
    def __config(self, ip, port):
        self.nodes = urllib2.urlopen('http://cs.ucsb.edu/~dkudrow/cs271/nodes').read().splitlines()
        #self.nodes = [
                #'127.0.0.1:6000',
                #'127.0.0.1:6001',
                #'127.0.0.1:6002',
                #'127.0.0.1:6003',
                #'127.0.0.1:6004' ]
        self.pid = self.nodes.index(ip + ':' + port)

    # Initialize Paxos instance
    def __init__(self, ip, port):
        self.proposal_number = 0
        self.max_prepared = -1
        self.max_accepted = -1
        self.accepted_value = 0
        self.__config(ip, port)

    def send_prepare(self, value):
        self.proposal_number += 1
        data = {}
        data['msg_type'] = 'prepare'
        data['pid'] = str(self.pid)
        data['proposal_number'] = str(self.proposal_number)
        resp = self.__broadcast(data)
        max_accepted = -1
        for key in iter(resp):
            data = json.loads(resp[key])
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
        resp['pid'] = str(self.pid)
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
        data['pid'] = str(self.pid)
        data['proposal_number'] = str(self.proposal_number)
        data['value'] = value
        resp = self.__broadcast(data)
        for key in iter(resp):
            data = json.loads(resp[key])
            if data['accepted'] != 'yes':
                print '))) accept(%d) rejected by node %s' % (self.proposal_number, key)
                return -1
        print '))) value %s chosen' % (value)
        return value

    def recv_accept(self, data):
        resp = {}
        resp['msg_type'] = 'accept'
        resp['pid'] = str(self.pid)
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

