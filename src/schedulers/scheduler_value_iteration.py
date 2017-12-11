import numpy as np
from collections import OrderedDict
from environment import State

import pdb

# Action constants
NOP = 0
SCHEDULE = 1

class SchedulerValueIteration:
    def __init__(self, config, job_gen, data_path):
        self.config = config
        self.job_gen = job_gen
        self.data_path = data_path

        self.line_type = "offline"
        self.Q_func = None

        # Job generator must be uniform
        if not job_gen.dist_name == "Uniform":
            raise ValueError("Parameter job_gen must be a uniform distribution")

           
    def train(self, train_sequences=None):
        # Initialize offline learning
        new_prob = self.job_gen.dist_params["new"]
        low = self.job_gen.dist_params["low"]
        high = self.job_gen.dist_params["high"]

        Q = OrderedDict()
        next_table = OrderedDict()

        job_arrivals = [0] + [i for i in range(low, high+1)]
        job_types = [0] + [i for i in range(low, high+1)]

        idle_next_states = []
        for job_arrival in job_arrivals:
            state = (job_arrival, (0, 0))
            idle_next_states.append(state)

        sched_next_states = {}
        for job_type in job_types:
            sched_same_job_states = []
            if job_type != 0:
                for job_arrival in job_arrivals:
                    state = (job_arrival, (job_type, job_type-1))
                    sched_same_job_states.append(state)
            sched_next_states[job_type] = sched_same_job_states

        inter_next_states = {}
        for job_type in job_types:
            inter_same_job_states = {}
            for time_rem in range(job_type-1, 0, -1):
                inter_same_time_states = []
                for job_arrival in job_arrivals:
                    state = (job_arrival, (job_type, time_rem))
                    inter_same_time_states.append(state)
                inter_same_job_states[time_rem] = inter_same_time_states
            inter_next_states[job_type] = inter_same_job_states

        probabilities = {}
        for job_arrival in job_arrivals:
            if job_arrival == 0:
                probabilities[job_arrival] = new_prob
            else:
                probabilities[job_arrival] = new_prob / (high - low + 1)
        print(probabilities)

        all_states = []
        for job_arrival in job_arrivals:
            # Idle states
            state = (job_arrival, (0, 0))
            Q[state] = [0, 0]
            all_states.append(state)

            # Action schedule
            next_states = idle_next_states
            idle_nop_nexts = []
            for next_state in next_states:
                prob = probabilities[next_state[0]]
                reward = next_state[1][0]
                next = (next_state, prob, reward)
                idle_nop_nexts.append(next)

            # Action nothing
            next_states = sched_next_states[job_arrival]
            idle_schedule_nexts = []
            for next_state in next_states:
                prob = probabilities[next_state[0]]
                reward = next_state[1][0]
                next = (next_state, prob, reward)
                idle_schedule_nexts.append(next)

            next_table[state] = {
                NOP: idle_nop_nexts,
                SCHEDULE: idle_schedule_nexts,
            }

            # Active states
            for job_type in job_types:
                for time_rem in range(job_type-1, 0, -1):
                    state = (job_arrival, (job_type, time_rem))
                    Q[state] = [0, 0]
                    all_states.append(state)

                    if time_rem > 1:
                        next_states = inter_next_states[job_type][time_rem]
                    else:
                        next_states = idle_next_states

                    nexts = []
                    for next_state in next_states:
                        prob = probabilities[next_state[0]]
                        reward = next_state[1][0]
                        next = (next_state, prob, reward)
                        nexts.append(next)

                    next_table[state] = {
                        NOP: nexts,
                        SCHEDULE: [],
                    }

        # Constants
        epsilon = 0.001
        gamma = 0.8

        # Value iteration 
        iterations = 0
        delta =  epsilon
        while delta >= epsilon:
            delta = 0
            for state, actions in Q.items():
                for action, Q_sa in enumerate(actions):
                    # Iterate over all next actions
                    next_states = next_table[state][action]
                    for next_state, prob, reward in next_states:
                        Q[state][action] = prob * (reward + gamma *
                                max(Q[next_state]))
                    
                    delta = max(delta, abs(Q_sa - Q[state][action]))

            iterations += 1
            print(iterations, delta)

        print("Complete")
        print(len(Q))
        print(Q)

        self.Q_func = Q

    def evaluate(self, state):
        actions = self.Q_func[state]
        max_action = np.argmax(actions)
        return max_action


