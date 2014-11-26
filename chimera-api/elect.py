#
# elect.py -- leader election with ring algorithm
#

import json
import debug

class Elect:
    def __init__(self, message):
        self.message = message
        if self.message == 1:
            debug.trigger('self.message initialized to 1 in elect.py')

    def __msg_send(self, pid, data):
        return self.message.msg_send(pid, '/elect', data)

    # return next pid in ring
    def __next_pid(self, pid):
        return (pid + 1) % 5

    # initiate an election and return the result
    def elect(self):
        leader = self.send_elect(self.message.pid, self.message.pid)
        return leader

    # send an election message to the next node in the ring
    def send_elect(self, initiator, max_pid):
        next_pid = self.__next_pid(self.message.pid)
        while next_pid != initiator:
            data = {}
            data['msg_type'] = 'elect'
            data['initiator'] = str(initiator)
            data['max_pid'] = str(max_pid)
            resp = json.loads(self.__msg_send(next_pid, data))
            if resp['status'] == 'ok':
                max_pid = resp['max_pid']
                break
            next_pid = self.__init__(next_pid)
        return int(max_pid)

    # propogate an election message
    def recv_elect(self, data):
        max_pid = max(self.message.pid, int(data['max_pid']))
        max_pid = self.send_elect(int(data['initiator']), max_pid)
        resp = {}
        resp['msg_type'] = 'elect'
        resp['max_pid'] = str(max_pid)
        return resp

