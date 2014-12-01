#
# messenger.py -- message passing and node configuration
#

import json
import urllib
import urllib2

import logging
FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

class Messenger:
    def __node_config(self, ip, port):
        try:
            self.nodes = urllib2.urlopen('http://cs.ucsb.edu/~dkudrow/cs271/nodes').read().splitlines()
        except:
            self.nodes = [ '127.0.0.1:6001',
                           '127.0.0.1:6002',
                           '127.0.0.1:6003',
                           '127.0.0.1:6004',
                           '127.0.0.1:6005' ]

        self.pid = self.nodes.index(ip + ':' + port)

    def __init__(self, port):
        self.__node_config('127.0.0.1', port)
        self.node_count = len(self.nodes)
        self.majority = len(self.nodes)/2

    # Send message to the next 'maj' nodes
    def broadcast_majority(self, data, route):
        responses = {}
        
        num_ok_resp = 0
        pid = self.pid
        while num_ok_resp != self.majority:
            pid = (pid + 1) % self.node_count
            if pid == self.pid:
                return {}

            response = json.loads(self.send_message(pid, route, data))
            if response['status'] == 'ok':
                logging.info('Got OK from server {0}'.format(pid))

                num_ok_resp += 1
                responses[pid] = response

        return responses

    # Send message 'data' to 'host'
    def send_message(self, pid, route, data):
        host = self.nodes[pid]
        data['pid'] = str(self.pid)
        url = 'http://' + host + route

        # cannot handle multidimensional hash/arrays
        encoded_data = urllib.urlencode({'json_data_string': json.dumps(data)})

        req = urllib2.Request(url, encoded_data)
        try:
            resp = urllib2.urlopen(req).read()
        except urllib2.URLError, e:
            resp = json.dumps({'status':str(e.errno)})
        return resp
