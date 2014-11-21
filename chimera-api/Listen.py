#!env/bin/python
# Listen.py -- RESTful API for Chimera

import json
import flask
import Chimera
import sys

chimera = Chimera.Chimera(sys.argv[1])
app = flask.Flask(__name__)

@app.route('/')
def alive():
    return 'Chimera node is running'

# Public API
@app.route('/withdraw/<amount>')
def withdraw(amount):
    status = chimera.handleWithdraw(int(amount))
    return json.dumps({'status':status})

@app.route('/deposit/<amount>')
def deposit(amount):
    status = chimera.handleDeposit(int(amount))
    return json.dumps({'status':status})

@app.route('/balance')
def balance():
    status = chimera.handleBalance()
    return json.dumps({'status':status})

@app.route('/fail')
def fail():
    status = chimera.handleFail()
    return json.dumps({'status':status})

@app.route('/unfail')
def unfail():
    status = chimera.handleUnfail()
    return json.dumps({'status':status})

# Internal Paxos messages
@app.route('/paxos')
def prepare():
    data = flask.request.args
    resp = chimera.handlePaxos(data)
    return resp

# Internal leader election messages
@app.route('/election')
def election():
    status = chimera.handleElection()
    return json.dumps({'status':status})
         
if __name__ == '__main__':
    app.run(port=int(sys.argv[1]), debug=True)
