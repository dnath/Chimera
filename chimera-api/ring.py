import json

class Ring:
    def __init__(self, message):
        self.message = message

    def __msg_send(self, pid, data):
        return self.message.msg_send(pid, '/elect', data)

    def elect(self):
        return self.send_elect(self.message.pid, self.message.pid)

    def send_elect(self, initiator, max_pid):
        next_pid = self.message.pid + 1
        while next_pid != initiator:
            data = {}
            data['msg_type'] = 'elect'
            data['initiator'] = str(initiator)
            data['max_pid'] = str(max_pid)
            resp = json.loads(self.__msg_send(next_pid, data))
            if resp['status'] == 'ok':
                max_pid = resp['max_pid']
                break
            next_pid = (next_pid + 1) % 5
        return int(max_pid)

    def recv_elect(self, data):
        max_pid = max(self.message.pid, data['max_pid'])
        return self.send_elect(data['initiator'], max_pid)

