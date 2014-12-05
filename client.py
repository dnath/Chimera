#!env/bin/python

import logging
import urllib2
import re
import json
import pprint
import sys

class ClientCli:
    def __init__(self, server_address):
        self.server_address = server_address

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
        status = 'failed'
        balance = None

        server_url = 'http://{0}'.format(self.server_address) + route
        request = urllib2.Request(server_url)

        try:
            response = urllib2.urlopen(request).read()
        except urllib2.URLError, e:
            response = json.dumps({'status': str(e.errno)})

        response = json.loads(response)
        logging.info('response = \n{0}'.format(pprint.pformat(response)))

        if response['status'] == 'ok':
            status = 'ok'

        if route == '/balance':
            balance = response['balance']

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

    try:
        server_address = sys.argv[1]
    except:
        server_address = raw_input('Please provide server address (www.xxx.yyy.zzz:pppp):')

    ClientCli(server_address).run()