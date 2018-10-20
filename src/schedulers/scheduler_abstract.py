from abc import ABC, abstractmethod

class SchedulerAbstract:
    def __init__(self, config):
        self.config = config

        self.line_type = None

    @abstractmethod
    def train(self, *args):
        pass

    @abstractmethod
    def evaluate(self, *args):
        pass
