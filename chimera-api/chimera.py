#
# chimera.py -- top level event handlers
#

import json
import pprint
import logging

FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

from elector import Elector
from messenger import Messenger
#from paxos.basic_paxos import Paxos
from paxos.multi_paxos import Paxos
import log

class Chimera:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.messenger = Messenger(host=host, port=port)
        self.pid = self.messenger.pid

        self.paxos = Paxos(self.messenger)

        # self.elector = Elector(self.messenger)
        # self.leader_pid = self.elector.elect()
        # self.leader = self.messenger.nodes[self.leader_pid]
        #
        # logging.info('Elected Leader: [%s] %s' % (self.leader_pid, self.leader))

        self.log = log.Log()
        self.first_unchosen_index = 0

    def is_leader(self):
        # return self.pid == self.leader_pid
        return False

    def __send_transaction(self, log_entry):
        logging.info('log_entry = {0}'.format(log_entry))
        response = {}

        while True:
            prepare_result = self.paxos.send_prepare(paxos_index=self.first_unchosen_index,
                                             value=log_entry)
            if prepare_result['return_code']:
                prepared_value = prepare_result['prepared_value']
                logging.info('send_prepare was successful, prepared_value = {0}!'.format(prepared_value))
                logging.info('Is prepared value changed = {0}'.format(prepare_result['is_value_changed']))

                accept_result = self.paxos.send_accept(paxos_index=self.first_unchosen_index)

                if accept_result:
                    logging.info('send_accept was successful!')
                    self.log.put(log_index=self.first_unchosen_index, log_entry=prepared_value)
                    logging.info("log =\n{0}".format(pprint.pformat(self.log.store)))
                    logging.info('"{0}" was chosen at log index {1}'.format(prepared_value, self.first_unchosen_index))

                    self.first_unchosen_index += 1
                    logging.info('incremented first_unchosen_index, first_unchosen_index = {0}'.format(self.first_unchosen_index))

                    if prepare_result['is_value_changed'] == False:
                        response['log_entry'] = prepared_value
                        response['log_index'] = self.first_unchosen_index - 1

                        logging.info("Done.")
                        break
                    else:
                        logging.info(
                            "Trying again with new first_unchosen_index = {0}".format(self.first_unchosen_index))
                        continue
                else:
                    logging.info('send_accept failed!')
            else:
                logging.info('send_prepare failed!')

        return response

    def handle_withdraw(self, amount):
        log_entry = 'W {0}'.format(amount)
        response = self.__send_transaction(log_entry)
        logging.info('response = {0}'.format(response))
        return json.dumps(response)

    def handle_deposit(self, amount):
        log_entry = 'D {0}'.format(amount)
        response = self.__send_transaction(log_entry)
        logging.info('response = {0}'.format(response))
        return json.dumps(response)

    def handle_balance(self):
        response = {}
        logging.info('log = \n{0}'.format(pprint.pformat(self.log.store)))
        response['log'] = dict(self.log.store)
        return json.dumps(response)

    def handle_fail(self):
        return 'ok'

    def handle_unfail(self):
        return 'ok'

    def handle_paxos(self, data_json):
        response = {}

        if data_json['msg_type'] == 'prepare':
            response = self.paxos.recv_prepare(data_json)
        if data_json['msg_type'] == 'accept':
            response = self.paxos.recv_accept(data_json)

        response['status'] = 'ok'

        return json.dumps(response)

    def handle_elect(self, data):
        response = {}

        # if data['msg_type'] == 'elect':
        #     response = self.elector.recv_elect(data)
        #     self.leader_pid = int(response['max_pid'])
        #     logging.info('Elected Leader: %s' % (self.messenger.nodes[self.leader_pid]))
        #
        # response['status'] = 'ok'

        return json.dumps(response)

    def handle_leader(self):
        response = {}
        # response['leader'] = self.leader_pid
        # response['status'] = 'ok'
        return json.dumps(response)

    def handle_prepare(self, index, value):
        result = self.paxos.send_prepare(paxos_index=index, value=value)
        logging.info('result from send_prepare = \n{0}'.format(pprint.pformat(result)))

        paxos_instance = self.paxos.paxos_instances[index]

        response = {}
        if result['return_code']:
            response['prepared'] = 'yes'
            response['max_accepted'] = paxos_instance.max_accepted
            response['accepted_value'] = paxos_instance.accepted_value
        else:
            response['prepared'] = 'no'
            response['max_prepared'] = paxos_instance.max_prepared

        response['proposal_value'] = paxos_instance.proposal_value
        response['proposal_number'] = paxos_instance.proposal_number
        response['status'] = 'ok'

        return json.dumps(response)

    def handle_chosen_value(self, index):
        paxos_instance = self.paxos.paxos_instances[index]

        response = {}
        if paxos_instance.proposal_number is None:
            response['status'] = 'bad'
            response['chosen_value'] = None
        else:
            response['chosen_value'] = paxos_instance.proposal_value
            response['status'] = 'ok'

        return json.dumps(response)

    def handle_accept(self, index):
        result = self.paxos.send_accept(index)
        paxos_instance = self.paxos.paxos_instances[index]
        response = {}
        if result:
            response['accepted'] = 'yes'
        else:
            response['accepted'] = 'no'

        response['proposal_value'] = paxos_instance.proposal_value
        response['proposal_number'] = paxos_instance.proposal_number
        #response['max_prepared'] = paxos_instance.max_prepared
        #response['max_accepted'] = paxos_instance.max_accepted
        #response['accepted_value'] = paxos_instance.accepted_value
        response['status'] = 'ok'

        return json.dumps(response)




