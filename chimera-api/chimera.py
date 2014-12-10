#
# chimera.py -- top level event handlers
#

import json
import pprint
import logging

FORMAT = "[%(asctime)s] [%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

import time
import random
import uuid

# from elector import Elector
from messenger import Messenger
from paxos.multi_paxos import Paxos
import log

import checkpoint

class Chimera:
    MAX_MAJORITY_TRIALS = 5
    MAX_SLEEP_TIME = 5

    def __init__(self, host, port, node_list_url, recover_from_log=True):
        self.host = host
        self.port = port
        self.recover_from_log = recover_from_log

        self.messenger = Messenger(host=host, port=port, node_list_url=node_list_url)
        self.pid = self.messenger.pid

        self.paxos = Paxos(self.messenger, filename='paxos_{0}.pickle'.format(self.pid))

        # self.elector = Elector(self.messenger)
        # self.leader_pid = self.elector.elect()
        # self.leader = self.messenger.nodes[self.leader_pid]
        #
        # logging.info('Elected Leader: [%s] %s' % (self.leader_pid, self.leader))

        self.checkpoint = checkpoint.CheckPoint()
        self.log = log.Log(recover=self.recover_from_log, filename='log_{0}.pickle'.format(self.pid))
        self.first_unchosen_index = len(self.log.store)

        self.fail_mode = False

    def handle_log(self):
        response = {'status': 'ok',
                    'log': self.log.store}
        return json.dumps(response)

    def is_leader(self):
        # return self.pid == self.leader_pid
        return False

    def __execute_state_machine(self, start_log_index, end_log_index):
        partial_checkpoint = checkpoint.CheckPoint()
        partial_checkpoint.start_index = start_log_index

        for index in xrange(start_log_index, end_log_index + 1):
            log_entry = self.log.get(index)

            if log_entry['op'] == 'D':
                partial_checkpoint.balance += int(log_entry['amount'])
                partial_checkpoint.end_index = index

            elif log_entry['op'] == 'W':
                partial_checkpoint.balance -= int(log_entry['amount'])
                partial_checkpoint.end_index = index

            else:
                raise Exception('Invalid log entry = {0}'.format(log_entry))

        return partial_checkpoint

    def __update_checkpoint(self):
        logging.info('Updating checkpoint...')
        if self.checkpoint.end_index == self.first_unchosen_index - 1:
            return

        if self.checkpoint.start_index == -1:
            end_log_index = self.first_unchosen_index - 1
            self.checkpoint = self.__execute_state_machine(0, end_log_index)

        else:
            start_log_index = self.checkpoint.end_index + 1
            end_log_index = self.first_unchosen_index - 1
            partial_checkpoint = self.__execute_state_machine(start_log_index, end_log_index)
            self.checkpoint.end_index = partial_checkpoint.end_index
            self.checkpoint.balance += partial_checkpoint.balance

    def __send_transaction(self, log_entry):
        logging.info('log_entry = {0}'.format(log_entry))
        num_majority_trials = 1
        response = {}

        while True:
            logging.info('num_majority_trials = {0}'.format(num_majority_trials))
            if num_majority_trials > 1:
                sleep_seconds = random.randint(1, Chimera.MAX_SLEEP_TIME)
                logging.info('Sleeping for {0} seconds...'.format(sleep_seconds))
                time.sleep(sleep_seconds)

            if num_majority_trials > Chimera.MAX_MAJORITY_TRIALS:
                logging.error('Failed to get majority after {0} trials !'.format(Chimera.MAX_MAJORITY_TRIALS))
                response['status'] = 'failed'
                response['reason'] = 'No Majority after {0} trials !'.format(Chimera.MAX_MAJORITY_TRIALS)
                break

            prepare_result = self.paxos.send_prepare(paxos_index=self.first_unchosen_index, value=[log_entry])

            if prepare_result['return_code']:
                prepared_value = list(prepare_result['prepared_value'])
                logging.info('send_prepare was successful, prepared_value = {0}!'.format(prepared_value))
                logging.info('Is prepared value changed = {0}'.format(prepare_result['is_value_changed']))

                # Withdraw will always be single element list
                single_prepared_value = prepared_value[0]
                if single_prepared_value['op'] == 'W' and not prepare_result['is_value_changed']:
                    self.__update_checkpoint()
                    self.log.persist()
                    withdraw_value = int(single_prepared_value['amount'])
                    if self.checkpoint.balance < withdraw_value:
                        logging.error('Insufficient Funds = {balance}, withdraw_value = {value}!'.format(
                                                                                    balance=self.checkpoint.balance,
                                                                                    value=withdraw_value))
                        response['status'] = 'failed'
                        response['reason'] = 'Insufficient Funds!'
                        break

                accept_result = self.paxos.send_accept(paxos_index=self.first_unchosen_index, value=prepared_value)

                if accept_result['return_code']:
                    logging.info('send_accept was successful!')

                    for single_prepared_value in prepared_value:
                        self.log.put(log_index=self.first_unchosen_index, log_entry=single_prepared_value)
                        logging.info('"{0}" was chosen at log index {1}'.format(single_prepared_value, self.first_unchosen_index))
                        self.first_unchosen_index += 1
                        logging.info('incremented first_unchosen_index, first_unchosen_index = {0}'.format(self.first_unchosen_index))

                    logging.info("log =\n{0}".format(pprint.pformat(self.log.store)))

                    # we have inserted the actual operation into the log,
                    # we are done
                    if prepare_result['is_value_changed'] == False:
                        response['status'] = 'ok'
                        response['log_entry'] = prepared_value
                        response['log_index'] = self.first_unchosen_index - 1
                        self.__update_checkpoint()
                        self.log.persist()

                        logging.info("Done.")
                        break
                    else:
                        logging.info("Trying again with new first_unchosen_index = {0}".format(self.first_unchosen_index))
                        continue
                else:
                    logging.info("accept_result['got_majority'] = {0}".format(accept_result['got_majority']))
                    if accept_result['got_majority'] == False:
                        num_majority_trials += 1
                    logging.info('send_accept failed!')

            else:
                logging.info("prepare_result['got_majority'] = {0}".format(prepare_result['got_majority']))
                if prepare_result['got_majority'] == False:
                    num_majority_trials += 1
                logging.info('send_prepare failed!')

        return response

    def handle_withdraw(self, amount):
        if self.fail_mode:
            response = {'status': 'failed', 'reason': 'Fail Mode On'}
            return json.dumps(response)

        id = str(uuid.uuid4())
        log_entry = {'id': id, 'op': 'W', 'amount': amount}
        response = self.__send_transaction(log_entry)
        logging.info('response = {0}'.format(response))
        return json.dumps(response)

    def handle_deposit(self, amount):
        if self.fail_mode:
            response = {'status': 'failed', 'reason': 'Fail Mode On'}
            return json.dumps(response)

        id = str(uuid.uuid4())
        log_entry = {'id': id, 'op': 'D', 'amount': amount}
        response = self.__send_transaction(log_entry)
        logging.info('response = {0}'.format(response))
        return json.dumps(response)

    def handle_balance(self):
        if self.fail_mode:
            response = {'status': 'failed', 'reason': 'Fail Mode On'}
            return json.dumps(response)

        response = {}
        logging.info('log = \n{0}'.format(pprint.pformat(self.log.store)))

        self.__update_checkpoint()

        response['status'] = 'ok'
        response['balance'] = self.checkpoint.balance
        # response['log'] = self.log.store

        return json.dumps(response)

    def handle_fail(self):
        if self.fail_mode:
            response = {'status': 'failed', 'reason': 'Fail Mode On'}
            return json.dumps(response)

        self.fail_mode = True
        logging.info('fail_mode = {0}'.format(self.fail_mode))
        response = {'status': 'ok'}
        return json.dumps(response)

    def handle_unfail(self):
        self.fail_mode = False
        logging.info('fail_mode = {0}'.format(self.fail_mode))
        response = {'status': 'ok'}
        return json.dumps(response)

    def handle_paxos(self, data_json):
        if self.fail_mode:
            response = {'status': 'failed', 'reason': 'Fail Mode On'}
            return json.dumps(response)

        response = {}

        if data_json['msg_type'] == 'prepare':
            response = self.paxos.recv_prepare(data_json)
        if data_json['msg_type'] == 'accept':
            response = self.paxos.recv_accept(data_json)

        response['status'] = 'ok'

        return json.dumps(response)

    def handle_elect(self, data):
        if self.fail_mode:
            response = {'status': 'failed', 'reason': 'Fail Mode On'}
            return json.dumps(response)

        response = {}

        # if data['msg_type'] == 'elect':
        #     response = self.elector.recv_elect(data)
        #     self.leader_pid = int(response['max_pid'])
        #     logging.info('Elected Leader: %s' % (self.messenger.nodes[self.leader_pid]))
        #
        # response['status'] = 'ok'

        return json.dumps(response)

    def handle_leader(self):
        if self.fail_mode:
            response = {'status': 'failed', 'reason': 'Fail Mode On'}
            return json.dumps(response)

        response = {}
        # response['leader'] = self.leader_pid
        # response['status'] = 'ok'
        return json.dumps(response)

    def handle_prepare(self, index, value):
        if self.fail_mode:
            response = {'status': 'failed', 'reason': 'Fail Mode On'}
            return json.dumps(response)

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
        if self.fail_mode:
            response = {'status': 'failed', 'reason': 'Fail Mode On'}
            return json.dumps(response)

        paxos_instance = self.paxos.paxos_instances[index]

        response = {}
        if paxos_instance.proposal_number is None:
            response['status'] = 'bad'
            response['chosen_value'] = None
        else:
            response['chosen_value'] = paxos_instance.proposal_value
            response['status'] = 'ok'

        return json.dumps(response)

    def handle_accept(self, index, value):
        if self.fail_mode:
            response = {'status': 'failed', 'reason': 'Fail Mode On'}
            return json.dumps(response)

        result = self.paxos.send_accept(paxos_index=index, value=value)
        paxos_instance = self.paxos.paxos_instances[index]
        response = {}
        if result:
            response['accepted'] = 'yes'
        else:
            response['accepted'] = 'no'

        response['proposal_value'] = paxos_instance.proposal_value
        response['proposal_number'] = paxos_instance.proposal_number
        # response['max_prepared'] = paxos_instance.max_prepared
        # response['max_accepted'] = paxos_instance.max_accepted
        # response['accepted_value'] = paxos_instance.accepted_value
        response['status'] = 'ok'

        return json.dumps(response)




