#!env/bin/python

import json
import flask

app = flask.Flask(__name__)

@app.route('/')
def alive():
    return 'Chimera node is running'

@app.route('/message', methods=['POST'])
def recv_message():
    params = flask.request.form
    try:
        msg_type = params['msg_type']
        sender = params['sender']
        msg = params['msg']
        return 'msg_type: %s\nsender: %s\nmsg: %s\n' % (msg_type, sender, msg)
    except KeyError, e:
        return 'Invalid parameters'
         
if __name__ == '__main__':
    app.run()
