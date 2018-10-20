import numpy as np
from collections import OrderedDict
from environment import State
from .scheduler_abstract import SchedulerAbstract

class SchedulerValueIteration(SchedulerAbstract):
    def __init__(self, config, state_space):
        super().__init__(config)

        self.line_type = "offline"

        # Initialize Q_table
        states, actions, self.transition_table = state_space
        self.Q_table = OrderedDict()
        for state in states:
            self.Q_table[state] = OrderedDict()
            for action in actions:
                self.Q_table[state][action] = 0
        
    def train(self, train_params):
        # Constants
        epsilon = train_params["epsilon"]
        gamma = train_params["gamma"]

        # Value iteration
        iterations = 0
        delta = epsilon
        while delta >= epsilon:
            delta = 0
            for state, actions in self.Q_table.items():
                for action, Q_value in actions.items():
                    Q_up_value = 0
                    transitions = self.transition_table[state][action]
                    for next_state, probability, reward in transitions:
                        next_Q_values = list(self.Q_table[next_state].values())
                        Q_up_value += probability * (reward + gamma *
                                                     max(next_Q_values))

                    self.Q_table[state][action] = Q_up_value
                    delta = max(delta, abs(Q_value - self.Q_table[state][action]))

            iterations += 1
            print(iterations, delta)

        # Value iteration completed
        print("Complete, optimal Q-values are listed below for each state:")
        for state, actions in self.Q_table.items():
            state_str = "State " + str(state) + ": "
            for action, Q_value in actions.items():
                state_str += str(action) + " - " + str(Q_value) + ", "
            print(state_str)
           
    def evaluate(self, state):
        actions = self.Q_table[state]
        max_action = max(actions, key=actions.get)
        return max_action

