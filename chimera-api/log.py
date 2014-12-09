import logging
import pickle

class Log:
    def __init__(self, recover=True, filename='log.pickle'):
        self.filename = filename
        try:
            self.store = pickle.load(open(self.filename, 'r'))
        except:
            self.store = {}



    def put(self, log_index, log_entry):
        if self.store.has_key(log_index):
            logging.error('Log index {0} has been filled with "{1}"!', log_index, self.store[log_index])
            return False

        self.store[log_index] = log_entry

    def get(self, log_index):
        if not self.store.has_key(log_index):
            logging.error('Log index {0} is empty!', log_index)
            return None

        return self.store[log_index]

    def persist(self):
        pickle.dump(self.store, open(self.filename, 'w'))


