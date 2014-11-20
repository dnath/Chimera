#!env/bin/python
# Listen.py -- RESTful API for Chimera

import json
import flask
import Chimera

chimera = Chimera.Chimera()
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
@app.route('/prepare')
def prepare():
    params = flask.request.args
    try:
        status = chimera.handlePrepare()
    except KeyError:
        status = 'invalid_params'
    return json.dumps({'status':status})

@app.route('/accept')
def accept():
    params = flask.request.args
    try:
        status = chimera.handleAccept()
    except KeyError:
        status = 'invalid_params'
    return json.dumps({'status':status})

# Internal leader election messages
@app.route('/election')
def election():
    status = chimera.handleElection()
    return json.dumps({'status':status})
         
if __name__ == '__main__':
    app.run(debug=True)
