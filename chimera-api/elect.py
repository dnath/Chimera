#
# elect.py -- leader election
#

import json

class Elect:
    def __init__(self, message):
        self.message = message

    def __broadcast_next(self, data, maj=4):
        return self.message.broadcast_next(data, '/elect', maj)

    def elect(self):
        if self.send_elect():
            self.send_leader()

    def send_elect(self):
        print '))) Initiating election'
        data = {}
        data['msg_type'] = 'elect'
        resp = self.__broadcast_next(data, 5-self.message.pid-1 )
        for key in iter(resp):
            data = json.loads(resp[key])
            if data['status'] != 'ok':
                continue
            pid = int(data['pid'])
            if pid > self.message.pid:
                print '))) node %d forfeiting leadership to node %d' % (self.message.pid, pid)
                return False
        return True

    def recv_elect(self, data):
        pid = int(data['pid'])
        print '))) responding to election from node %d' % (pid)
        print '))) starting new election'
        self.elect()
        return { 'pid':self.message.pid }

    def send_leader(self):
        print '))) Broadcasting new leader'
        data = {}
        data['msg_type'] = 'leader'
        self.__broadcast_next(data)
