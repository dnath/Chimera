#
# elector.py -- leader election with ring algorithm
#

import json
import debug
import logging

FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


class Elector:
    def __init__(self, messenger):
        self.messenger = messenger
        if self.messenger == 1:
            debug.trigger('self.messenger initialized to 1 in elector.py')

    def __msg_send(self, pid, data):
        return self.messenger.send_message(pid, '/elect', data)

    # return next pid in ring
    def __next_pid(self, pid):
        return (pid + 1) % self.messenger.node_count

    # initiate an election and return the result
    def elect(self):
        leader = self.send_elect(initiator=self.messenger.pid, max_pid=self.messenger.pid)
        return leader

    # send an election message to the next node in the ring
    def send_elect(self, initiator, max_pid):
        next_pid = self.__next_pid(self.messenger.pid)
        while next_pid != initiator:
            data = {}
            data['msg_type'] = 'elect'
            data['initiator'] = str(initiator)
            data['max_pid'] = str(max_pid)

            response = json.loads(self.__msg_send(next_pid, data))
            if response['status'] == 'ok':
                max_pid = response['max_pid']
                break
            next_pid = self.__next_pid(next_pid)

        return int(max_pid)

    # propagate an election message
    def recv_elect(self, data):
        max_pid = max(self.messenger.pid, int(data['max_pid']))
        max_pid = self.send_elect(int(data['initiator']), max_pid)

        response = {}
        response['msg_type'] = 'elect'
        response['max_pid'] = str(max_pid)
        return response

