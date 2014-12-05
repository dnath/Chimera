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

if len(sys.argv) < 2:
    print sys.argv[0], 'server_address [node_list_url]'
    exit(-1)

address_segments = sys.argv[1].split(':')
if len(address_segments) == 1:
    host = '127.0.0.1'
    port = int(address_segments[0])
else:
    host = address_segments[0]
    port = int(address_segments[1])

logging.info('host = {host}, port = {port}'.format(host=host, port=port))

if len(sys.argv) == 3:
    node_list_url = sys.argv[2]
else:
    node_list_url = 'http://cs.ucsb.edu/~dkudrow/cs271/nodes'

logging.info('node_list_url = {0}'.format(node_list_url))

chimera_instance = chimera.Chimera(host=host, port=port, node_list_url=node_list_url)
app = flask.Flask(__name__)

@app.route('/')
def alive():
    return json.dumps({'status':'ok'})

# Public API
@app.route('/withdraw/<amount>')
def withdraw(amount):
    response = chimera_instance.handle_withdraw(int(amount))
    return response

@app.route('/deposit/<amount>')
def deposit(amount):
    response = chimera_instance.handle_deposit(int(amount))
    return response

@app.route('/balance')
def balance():
    response = chimera_instance.handle_balance()
    return response

@app.route('/fail')
def fail():
    response = chimera_instance.handle_fail()
    return response

@app.route('/unfail')
def unfail():
    response = chimera_instance.handle_unfail()
    return response

# Internal Paxos messages
@app.route('/paxos', methods=['POST'])
def paxos():
    data = flask.request.form
    data_json = json.loads(data['json_data_string'])
    response = chimera_instance.handle_paxos(data_json)
    return response

# Test route for paxos prepare
@app.route('/prepare/<index>/<value>')
def prepare(index, value):
    return chimera_instance.handle_prepare(index, value)

# Test route for paxos accept
@app.route('/accept/<index>')
def accept(index):
    return chimera_instance.handle_accept(index)

# Test route for paxos accept
@app.route('/chosen_value/<index>')
def chosen_value(index):
    return chimera_instance.handle_chosen_value(index)

# Internal leader election messages
@app.route('/elect', methods=['POST'])
def elect():
    data = flask.request.form
    data_json = json.loads(data['json_data_string'])
    response = chimera_instance.handle_elect(data_json)
    return response

@app.route('/leader')
def leader():
    return chimera_instance.handle_leader()
         
if __name__ == '__main__':
    debug.listen()
    app.run(host=host, port=port, debug=True)
