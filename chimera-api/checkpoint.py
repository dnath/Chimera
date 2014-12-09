import pickle
import logging

class CheckPoint:
    def __init__(self, filename='log.pickle'):
        self.filename = filename
        self.balance = 0
        self.start_index = -1
        self.end_index = -1
