#!env/bin/python

import logging
import urllib2
import re
import json
import pprint

class ClientCli:
    def __init__(self, server_config_url='http://cs.ucsb.edu/~dkudrow/cs271/nodes'):
        self.servers = self.__get_chimera_servers(server_config_url)
        self.leader = self.servers[-1]

    def __get_chimera_servers(self, server_config_url):
        try:
            nodes = urllib2.urlopen(server_config_url).read().splitlines()
        except:
            nodes = ['127.0.0.1:6001',
                     '127.0.0.1:6002',
                     '127.0.0.1:6003',
                     '127.0.0.1:6004',
                     '127.0.0.1:6005']

        return nodes

    def run(self):
        while True:
            command = raw_input('[chimera]')

            print command
            if re.match('^(((withdraw|deposit)\s+\d+)|balance\s*)$', command, re.IGNORECASE) is None:
                logging.info('Invalid Command = "{0}"!'.format(command))
                continue

            command_segments = command.split()
            if command_segments[0].lower() == 'deposit':
                amount = int(command_segments[1])
                self.__deposit(amount)
            elif command_segments[0].lower() == 'withdraw':
                amount = int(command_segments[1])
                self.__withdraw(amount)
            elif command_segments[0].lower() == 'balance':
                self.__balance()
            else:
                logging.info('Invalid command!')

    def __send_command_to_bank(self, route):
        current_leader = self.leader
        status = 'continue'
        balance = None

        while status == 'continue':
            server_url = 'http://{leader}'.format(leader=current_leader) + route
            request = urllib2.Request(server_url)
            try:
                response = urllib2.urlopen(request).read()
            except urllib2.URLError, e:
                response = json.dumps({'status': str(e.errno)})

            response = json.loads(response)
            logging.info('response = \n{0}'.format(pprint.pformat(response)))

            if response['status'] == 'ok':
                self.leader = current_leader
                status = 'ok'

                if route == '/balance':
                    balance = response['balance']

            elif response['status'] == 'forward':
                current_leader = response['leader']
                status = 'continue'
            else:
                old_leader_index = self.servers.index(current_leader)
                potential_leader = self.servers[(old_leader_index + 1) % len(self.servers)]

                if potential_leader == self.leader:
                    logging.info('Failed to find a leader!')
                    status = 'failed'
                else:
                    current_leader = potential_leader
                    status = 'continue'

        return status, balance

    def __deposit(self, amount):
        logging.info('amount = {0}'.format(amount))
        route = '/deposit/{amount}'.format(amount=amount)
        status, _ = self.__send_command_to_bank(route)
        if status == 'ok':
            print 'Deposit was successful!'

    def __withdraw(self, amount):
        logging.info('amount = {0}'.format(amount))
        route = '/withdraw/{amount}'.format(amount=amount)
        status, _ = self.__send_command_to_bank(route)
        if status == 'ok':
            print 'Withdrawal was successful!'

    def __balance(self):
        logging.info('Trying to get balance...')
        route = '/balance'
        status, balance = self.__send_command_to_bank(route)
        if status == 'ok':
            print 'Balance = {balance}'.format(balance)

if __name__ == '__main__':
    FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    ClientCli().run()
