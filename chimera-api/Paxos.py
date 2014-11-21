import json
import urllib
import urllib2

class Proposal:
    def __init__(self, proposal_number, pid, value):
        self.proposal_number = proposal_number
        self.pid = pid
        self.value = value

    def compare(self, rhs):
        if rhs.proposal_number < self.proposal_number:
            return False
        elif rhs.proposal_number > self.proposal_number:
            return True
        elif rhs.pid > self.pid:
            return True
        return False

class Paxos:
    def __msg_send(self, host, data):
        url = 'http://' + host + '/paxos'
        encoded_data = urllib.urlencode(data)
        req = urllib2.Request(url, encoded_data)
        resp = urllib2.urlopen(req)
        return resp.read()

    def __config(self, ip, port):
        self.nodes = [
                '127.0.0.1:6000',
                '127.0.0.1:6001',
                '127.0.0.1:6002',
                '127.0.0.1:6003',
                '127.0.0.1:6004']
        self.pid = self.nodes.index(ip + ':' + port)

    def __init__(self, ip, port):
        self.proposal_number = 0
        self.max_prepared = -1
        self.max_accepted = -1
        self.accepted_value = 0
        self.__config(ip, port)

    def send_prepare(self, value):
        # increment proposal number
        self.proposal_number += 1
        # prepare message
        data = {}
        data['msg_type'] = 'prepare'
        data['proposal_number'] = str(self.proposal_number)
        data['pid'] = str(pid)
        resp = {}
        # send message to next three hosts
        for i in range(1, 4):
            host = self.nodes[(self.pid + i) % 3]
            resp[i] = self.__msg_send(host, data)

        # get value from highest accepted proposal
        max_accepted = -1
        for key in iter(resp):
            data = json.loads(resp[key])
            # FIXME: check response
            if data['prepared'] == 'no':
                return -1
            if data['prepared'] == 'yes' and data['max_accepted'] > max_accepted: 
                max_accepted = data['max_accepted']
                value = data['value'] 

        return value

    def recv_prepare(self, data):
        resp = {}
        if data['proposal_number'] > self.max_prepared:
            self.max_prepared = data['proposal_number']
            resp['prepared'] = 'yes'
            resp['max_accepted'] = self.max_accepted
            resp['max_value'] = self.accepted_value
        else:
            resp['prepared'] = 'no'
            resp['max_prepared'] = self.max_prepared
        return resp
