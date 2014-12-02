#!env/bin/python
#!/usr/bin/python
#
# server.py -- RESTful API for Chimera
#
import logging
FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

import debug
import json
import flask
import sys
import chimera

addr = sys.argv[1].split(':')
if len(addr) == 1:
    host = '127.0.0.1'
    port = int(addr[0])
else:
    host = addr[0]
    port = int(addr[1])

logging.info('host = {host}, port = {port}'.format(host=host, port=port))

chimera_instance = chimera.Chimera(host=host, port=port)
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
    data_json = json.loads(data['json_data_string'])
    resp = chimera_instance.handle_paxos(data_json)
    return resp

# Test route for paxos prepare
@app.route('/prepare/<value>')
def prepare(value):
    return chimera_instance.handle_prepare(value)

# Test route for paxos accept
@app.route('/accept')
def accept():
    return chimera_instance.handle_accept()

# Test route for paxos accept
@app.route('/chosen_value')
def chosen_value():
    return chimera_instance.handle_chosen_value()

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
    app.run(host=host, port=port, debug=True)
