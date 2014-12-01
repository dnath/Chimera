#!/usr/bin/python
#
# test.py -- interactive test script
#

import json
import os
import signal
import subprocess
import sys
import types
import urllib2

nodes = []*5
procs = {}

# populate list of nodes
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

# decorator to run command for list of pids
def RunForPids(func):
    def run_for_pids(args, **kwargs):
        if type(args) != types.ListType:
            result = False
            try:
                pid = int(args)
                result = func(pid, **kwargs)
            except:
                print 'invalid argument: ', type(args), args
        else:
            result = {}
            for arg in args:
                try:
                    pid = int(arg)
                    result[pid] = func(pid, **kwargs)
                except:
                    print 'invalid argument: ', type(arg), arg
                    continue
        return result
    return run_for_pids

# hit a route on a node
@RunForPids
def send(pid, route='/'):
    host = nodes[pid]
    url = 'http://' + host + route
    try:
        return urllib2.urlopen(url).read()
    except:
        return json.dumps({'status':'bad'})

# start a node
@RunForPids
def start(pid):
    if ping(pid):
        return False
    path = os.getcwd() + '/listen.py'
    args = str(6001 + pid)
    procs[pid] = subprocess.Popen([path, args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
    return True

# ping a node
@RunForPids
def ping(pid):
    resp = json.loads(send(pid, route='/'))
    if resp['status'] != 'ok':
        return False
    return True

# stop a node, write output to logfile
@RunForPids
def stop(pid):
    try:
        os.killpg(procs[pid].pid, signal.SIGTERM)
    except:
        return False
    if procs[pid].poll() == None:
        logfile = open('node_%d.log' % pid, 'w')
        for l in procs[pid].stdout.readlines():
            logfile.write(l)
        return True
    return False

# kill all nodes and write output to log files
def cleanup():
    for pid in iter(procs):
        pid = int(pid)
        if procs[pid].poll() == None:
            stop(pid)

# interactive loop
def loop():
    cont = True
    while (cont):
        args = raw_input('> ').split()
        if len(args) < 1: continue
        if args[-1] == 'all': args = args[:-1] + ['0', '1', '2', '3', '4']
        if args[0] == 'help':
            print '''
            help                                --      this message
            start <pid pid ... | all>           --      start nodes
            ping <pid pid ... | all>            --      ping nodes
            stop <pid pid ... | all>            --      terminate nodes
            send <route> <pid pid ... | all>    --      hit <route> on nodes
            exit                                --      kill all nodes, write logs and exit
            '''
            continue
        if args[0] == 'exit':
            print 'Writing logs, good bye.'
            cleanup()
            cont = False
            continue
        if args[0] == 'start':
            result = start(args[1:])
            for pid in iter(result):
                if result[pid]:
                    print 'started node %d' % pid
                else:
                    print 'could not start node %d' % pid
            continue
        if args[0] == 'ping':
            result = ping(args[1:])
            for pid in iter(result):
                if result[pid]:
                    print 'node %d is up' % pid
                else:
                    print 'node %d is down' % pid
            continue
        if args[0] == 'stop':
            result = stop(args[1:])
            for pid in iter(result):
                if result[pid]:
                    print 'stopped node %d' % pid
                else:
                    print 'could not stop node %d' % pid
            continue
        if args[0] == 'send':
            result = send(args[2:], route='/'+args[1])
            for pid in iter(result):
                    print '%d: %s' % (pid, result[pid])
            continue

        print 'invalid command'

# catch ^C interrupts
def sigint_handler(signal, frame):
    print 'Writing logs, good bye.'
    cleanup()
    sys.exit(0)

if __name__ == '__main__':
    nodes = get_nodes()
    signal.signal(signal.SIGINT, sigint_handler)
    loop()
