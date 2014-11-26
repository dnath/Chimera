#!env/bin/python
#
# listen.py -- RESTful API for Chimera
#

import debug
import json
import flask
import sys
import chimera

chimera_instance = chimera.Chimera(sys.argv[1])
app = flask.Flask(__name__)

@app.route('/')
def alive():
    return json.dumps({'status':'ok'})

# Public API
@app.route('/withdraw/<amount>')
def withdraw(amount):
    status = chimera_instance.handle_withdraw(int(amount))
    return json.dumps({'status':status})

@app.route('/deposit/<amount>')
def deposit(amount):
    status = chimera_instance.handle_deposit(int(amount))
    return json.dumps({'status':status})

@app.route('/balance')
def balance():
    status = chimera_instance.handle_balance()
    return json.dumps({'status':status})

@app.route('/fail')
def fail():
    status = chimera_instance.handle_fail()
    return json.dumps({'status':status})

@app.route('/unfail')
def unfail():
    status = chimera_instance.handle_unfail()
    return json.dumps({'status':status})

# Internal Paxos messages
@app.route('/paxos', methods=['POST'])
def paxos():
    data = flask.request.form
    resp = chimera_instance.handle_paxos(data)
    return resp

# Test route for paxos prepare
@app.route('/prepare/<value>')
def prepare(value):
    return chimera_instance.handle_prepare(value)

# Test route for paxos accept
@app.route('/accept/<value>')
def accept(value):
    return chimera_instance.handle_accept(value)

# Internal leader election messages
@app.route('/elect', methods=['POST'])
def elect():
    data = flask.request.form
    resp = chimera_instance.handle_elect(data)
    return resp

@app.route('/leader')
def leader():
    return chimera_instance.handle_leader()
         
if __name__ == '__main__':
    debug.listen()
    app.run(port=int(sys.argv[1]), debug=True)
