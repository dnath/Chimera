#!/usr/bin/python
#
# test.py -- interactive test script
#

import json
import os
import signal
import subprocess
import urllib2

nodes = []*5
procs = {}

def get_nodes():
    try:
        resp = urllib2.urlopen('http://cs.ucsb.edu/~dkudrow/cs271/nodes')
        raw = resp.read()
        return raw.splitlines()
    except:
        return [
                '127.0.0.1:6001',
                '127.0.0.1:6002',
                '127.0.0.1:6003',
                '127.0.0.1:6004',
                '127.0.0.1:6005' ]
        vim_indentation_sucks = True

def send_msg(pid, route):
    host = nodes[pid]
    url = 'http://' + host + route
    try:
        return urllib2.urlopen(url).read()
    except:
        return json.dumps({'status':'bad'})

def start(pid):
    if ping(pid):
        return 'node %d already up' % (pid)
    path = os.getcwd() + '/listen.py'
    print path
    args = str(6001 + pid)
    procs[pid] = subprocess.Popen([path, args])
    return 'node %d started with pid %d' % (pid, procs[pid].pid)

def ping(pid):
    resp = json.loads(send_msg(pid, '/'))
    if resp['status'] != 'ok':
        return False
    return True

def stop(pid):
    try:
        procs[pid].terminate()
    except:
        return 'could not terminate node %d' % (pid)
    return 'terminated node %d' % (pid)

def loop():
    cont = True
    while (cont):
        args = raw_input('> ').split()
        if len(args) < 1:
            continue
        if args[0] == 'help':
            print '''
            help            --      this message
            start <pid>     --      start node <pid>
            ping <pid>      --      ping node <pid>
            stop <pid>      --      terminate node <pid>
            <pid> <route>   --      hit <route> on node <pid>
            exit            --      exit test loop
            '''
            continue
        if args[0] == 'exit':
            print 'Good bye.'
            cont = False
            continue
        if args[0] == 'start':
            try:
                pid = int(args[1])
                print start(pid)
            except IndexError:
                print 'Usage: start <pid>'
        if args[0] == 'ping':
            try:
                pid = int(args[1])
                msg = 'node %d is ' % (pid)
                if ping(pid):
                    msg += 'up'
                else:
                    msg += 'down'
                print msg
            except IndexError:
                print 'Usage: start <pid>'
                continue
        if args[0] == 'stop':
            try:
                pid = int(args[1])
                print stop(pid)
                continue
            except IndexError:
                print 'Usage: start <pid>'

if __name__ == '__main__':
    nodes = get_nodes()
    loop()
