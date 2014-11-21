# Chimera.py

import Paxos

class Chimera:
    def __init__(self, port):
        self.paxos = Paxos.Paxos('127.0.0.1', port)

    def handleWithdraw(self, amount):
        return 'ok'

    def handleDeposit(self, amount):
        return 'ok'

    def handleBalance(self):
        return 'ok'

    def handleFail(self):
        return 'ok'

    def handleUnfail(self):
        return 'ok'

    def handlePaxos(self, data):
        if data['msg_type'] == 'prepare':
            resp = paxos.recv_prepare(data)
        resp['status'] = 'ok'
        return json.dumps(resp)

    def handleElection(self):
        return 'ok'
