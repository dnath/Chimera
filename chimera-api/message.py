#
# message.py -- message passing and node configuration
#

import json
import urllib
import urllib2

class Message:
    def __node_config(self, ip, port):
        self.nodes = urllib2.urlopen('http://cs.ucsb.edu/~dkudrow/cs271/nodes').read().splitlines()
        #self.nodes = [
                #'127.0.0.1:6000',
                #'127.0.0.1:6001',
                #'127.0.0.1:6002',
                #'127.0.0.1:6003',
                #'127.0.0.1:6004' ]
        self.pid = self.nodes.index(ip + ':' + port)

    def __init__(self, port):
        self.__node_config('127.0.0.1', port)

    # Send message to the next 'maj' nodes
    def broadcast_next(self, data, route, maj):
        resp = {}
        for i in range(1, maj+1):
            host = self.nodes[(self.pid + i) % 5]
            print '))) broadcasting to %s' % (host)
            resp[i] = self.msg_send(host, route, data)
        return resp

    # Send message 'data' to 'host'
    def msg_send(self, host, route, data):
        data['pid'] = str(self.pid)
        url = 'http://' + host + route
        encoded_data = urllib.urlencode(data)
        req = urllib2.Request(url, encoded_data)
        try:
            resp = urllib2.urlopen(req).read()
        except urllib2.URLError, e:
            resp = json.dumps({'status':str(e.errno)})
        return resp
