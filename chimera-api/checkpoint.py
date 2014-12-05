import pickle
import logging

class CheckPoint:
    def __init__(self):
        self.balance = 0
        self.start_index = -1
        self.end_index = -1

    def load(self, filename='checkpoint.pickle'):
        return pickle.load(filename)

    def persist(self, filename='checkpoint.pickle'):
        pickle.dump(self, filename)
