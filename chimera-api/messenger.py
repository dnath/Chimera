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
    def __init__(self, host, port, node_list_url):
        self.host = host
        self.port = port

        self.nodes = self.__get_node_list(node_list_url)
        self.node_count = len(self.nodes)
        self.majority = len(self.nodes) / 2

        self.private_address = "{host}:{port}".format(host=host, port=port)
        self.pid = self.__get_pid(self.private_address)

    def __get_pid(self, private_address):
        for pid, node in enumerate(self.nodes):
            if node['private_address'] == private_address:
                return pid
        return -1

    def __get_node_list(self, node_list_url):
        try:
            nodes = json.loads(urllib2.urlopen(node_list_url).read())
        except:
            nodes = [{"public_address": "127.0.0.1:6001", "private_address": "127.0.0.1:6001", "region": "local"},
                     {"public_address": "127.0.0.1:6002", "private_address": "127.0.0.1:6002", "region": "local"},
                     {"public_address": "127.0.0.1:6003", "private_address": "127.0.0.1:6003", "region": "local"},
                     {"public_address": "127.0.0.1:6004", "private_address": "127.0.0.1:6004", "region": "local"},
                     {"public_address": "127.0.0.1:6005", "private_address": "127.0.0.1:6005", "region": "local"}]

        return nodes

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
        host = self.nodes[pid]['private_address']
        data['pid'] = str(self.pid)
        url = 'http://' + host + route

        logging.info('url = {0}'.format(url))

        # cannot handle multidimensional hash/arrays
        encoded_data = urllib.urlencode({'json_data_string': json.dumps(data)})

        request = urllib2.Request(url, encoded_data)
        try:
            response = urllib2.urlopen(request).read()
        except urllib2.URLError, e:
            logging.error(e.reason)
            response = json.dumps({'status': str(e.errno)})

        logging.debug('response =\n{0}'.format(response))

        return response
