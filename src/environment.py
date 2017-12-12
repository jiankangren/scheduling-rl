import logging
import numpy as np
from collections import OrderedDict
from itertools import permutations, product

import pdb
    
# TODO move this to main under __debug__
logger = logging.getLogger("Env-Logger")
hdlr = logging.FileHandler("../logs/log.txt")
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

class Machine():
    def __init__(self, mach_idx, mode):
        self.mach_idx = mach_idx
        self.mode = mode

        self.clear_internal_state()
        
    def clear_internal_state(self):
        self.current_job = None
        self.work_start_time = -1
        self.work_rem_time = -1
        self.work_end_time = -1
        self.reward = 0

    def load_job(self, job):
        if (self.mode == "non-preemptive" and self.current_job == None) or \
                self.mode == "preemptive":
            self.current_job = job

            self.work_start_time = job.arrival
            self.work_rem_time = job.duration
            self.work_end_time = job.departure

            if __debug__:
                log_str = "Machine %d scheduled job %d at time %d" % (self.mach_idx,
                        self.current_job.index, self.work_start_time)
                logger.debug(log_str)
            return True
        else:
            if __debug__:
                log_str = "Machine %d unable to schedule job %d at time %d" % \
                    (self.mach_idx, self.job.index, self.job.arrival)
            return False

    def get_state(self):
        if not self.current_job:
            return (0, 0)
        else:
            return (self.current_job.duration, self.work_rem_time)

    def is_idle(self):
        return (self.current_job == None)

    def unload_job(self):
        if __debug__:
            log_str = "Machine %d completed job %d at time %d" % (self.mach_idx,
                    self.current_job.index, self.work_end_time)

        self.work_start_time = -1
        self.work_rem_time = -1
        self.work_end_time = -1

        self.reward += self.current_job.value
        self.current_job = None
                
        return True

    def update_state(self):
        if self.current_job == None:
            return

        self.work_rem_time -= 1
        if self.work_rem_time == 0:
            self.unload_job()

# TODO use this
class State(list):
    def __init__(self, job_arrival, machines, time):
        super().__init__()

        mach_state = ((machine.current_job, machine.work_rem_time,) for
                machine in machines)
        self = (job_arrival, mach_state)


class Environment():
    def __init__(self, config, jobs, save_path, load_jobs):
        self.save_path = save_path
        self.config = config["environment"]

        # Init machines
        schedule_mode = config["common"]["schedule_mode"]
        num_machines = self.config["num_machines"]
        self.machines = [Machine(i, schedule_mode) for i in range(num_machines)]

        # FIXME
        # Generate all states, transitions, and rewards for offline
        """
        train_mode = config["common"]["train_mode"]
        if train_mode == "offline":
            dist_params = config["job_generator"]["parameters"]
            self.generate_state_space(dist_params, num_machines)
        """

    def _get_next_states(type, state, action, all_state, job_arrivals):
        pass

    # FIXME only works with Uniform and non-preemptive now
    # FIXME for offline need to generate everything but for online I only need
    # to generate the states and return
    def generate_state_space(self, dist_params, num_machines):
        # Obtain distribution parameters
        new_prob = dist_params["new"]
        low = dist_params["low"]
        high = dist_params["high"]
        func = eval(dist_params["func"])

        job_types = [0] + [i for i in range(low, high+1)]

        # Compute probabilites
        probabilities = {}
        for job_type in job_types:
            if job_type == 0:
                probabilities[job_type] = new_prob
            else:
                probabilities[job_type] = (1 - new_prob) / (high - low + 1)

        # Compute actions
        actions = [(0, -1)]
        for i in range(num_machines):
            actions.append((1, i))

        # Determine intermediate machine states
        inter_mach_states = [(0, 0)]
        for job_type in job_types:
            for rem_time in range(job_type-2, 0, -1):
                mach_state = (job_type, rem_time)
                inter_mach_states.append(mach_state)

        # Determine scheduled machine states
        sched_mach_states = []
        for job_type in job_types[1:]:
            mach_state = (job_type, job_type-1)
            sched_mach_states.append(mach_state)

        # Determine set of machine states corresponding to a 'schedule' action.
        # This is computed by taking the permutation of n-1 intermediate machine
        # states, including a single scheduled machine state, and finally taking
        # a permutation of the combined machine state.
        permute_inter_mach_states = list(product(inter_mach_states,
                                                 repeat=num_machines-1))

        combined_mach_states = []
        for pims in permute_inter_mach_states:
            for sms in sched_mach_states:
                combined_mach_state = (sms,) + pims
                combined_mach_states.append(combined_mach_state)

        permute_combined_mach_states = []
        for cms in combined_mach_states:
            permute_combined_mach_state = list(permutations(cms))
            permute_combined_mach_states.extend(permute_combined_mach_state)

        # Determine the set of machine states corresponding to a 'nop' action
        permute_nop_states = list(product(inter_mach_states, repeat=num_machines))

        # Combine all states together
        all_mach_states = permute_combined_mach_states + permute_nop_states
        all_complete_states = []
        for mach_state in all_mach_states:
            for job_type in job_types:
                complete_state = (job_type,) + (mach_state,)
                all_complete_states.append(complete_state)

        # Create a state action transition table
        transition_table = OrderedDict()
        for state in all_complete_states:
            transition_table[state] = OrderedDict()
            for action in actions:
                # FIXME make the 'non-preemptive' part general
                next_transitions = self._get_next_transitions("non-preemptive",
                        state, all_complete_states, action, probabilities, 
                        job_types, func)
                transition_table[state][action] = next_transitions

        # FIXME remove this
        for state, actions in transition_table.items():
            for action, transitions in actions.items():
                print(state, action, transitions)

        # Return all information
        return (all_complete_states, actions, transition_table)

        """
        # FIXME this may have to be changed, at the moment job_arrivals = job_types
        job_arrivals = [0] + [i for i in range(low, high+1)]
        job_types = [0] + [i for i in range(low, high+1)]

        # Transitions to idle states
        idle_next_states = []
        idle_machines = tuple([(0, 0) for i in range(num_machines)])
        for job_arrival in job_arrivals:
            state = (job_arrival, idle_machines)
            idle_next_states.append(state)

        # Transitions to scheduled jobs
        scheduled_next_states = {}
        """

    def _get_next_transitions(self, type, state, all_states, action,
            probabilities, job_arrivals, func):
        # FIXME
        if not type == "non-preemptive":
            raise NotImplementedError("Only 'non-preemptive' is completed")

        next_mach_states = []
        reward = 0

        # NOP action
        if action[0] == 0:
            for mach_state in state[1]:
                up_mach_state = tuple(np.subtract(mach_state, (0, 1)))
                if up_mach_state[1] <= 0:
                    reward += func(up_mach_state[0])
                    up_mach_state = (0, 0)
                next_mach_states.append(up_mach_state)

        # SCHEDULE action
        else:
            sched_mach_idx = action[1]

            # No arriving job
            if state[0] == 0:
                return []
            # FIXME this is only for non-preemptive
            elif not state[1][sched_mach_idx] == (0, 0):
                return [] 
            else:
                for mach_idx, mach_state in enumerate(state[1]):
                    if mach_idx == sched_mach_idx:
                        up_mach_state = (state[0], state[0] - 1)
                    else:
                        up_mach_state = tuple(np.subtract(mach_state, (0, 1)))
                        if up_mach_state[1] <= 0:
                            reward += func(up_mach_state[0])
                            up_mach_state = (0, 0)

                    next_mach_states.append(up_mach_state)

        # Determine the full state, probabilities, and rewards
        next_mach_states = tuple(next_mach_states)
        transitions = []
        for job_arrival in job_arrivals:
            next_state = (job_arrival, next_mach_states)
            probability = probabilities[job_arrival]
            transition = (next_state, probability, reward)
            transitions.append(transition)

        return transitions

    # FIXME simulation will have to be different for training/evaluating. For
    # simplicity, it might be better to create separate functions (even though
    # they are somewhat similar)
    def evaluate(self, job_sequences, num_sequences, scheduler):
        # FIXME make this a single number rather than a vector to save space
        rewards = []

        # FIXME need to iterate till the longest time
        # FIXME need to clear machines after every instance
        # Iterate through all sequences in an episode
        for _ in range(num_sequences):
            job_sequence = next(job_sequences)

            for machine in self.machines:
                machine.clear_internal_state()

            # Maximum simulation time
            time = 0
            job_idx = 0
            end_time = max(job_sequence, key=lambda x: x.departure).departure

            # Iterate through a job sequence
            while time < end_time:            
                if job_idx < len(job_sequence):
                    arriving_job = job_sequence[job_idx]
                    if arriving_job.arrival == time:
                        job_idx += 1
                    else:
                        arriving_job = None

                # Obtain state
                mach_states = []
                for machine in self.machines:
                    mach_state = machine.get_state()
                    mach_states.append(mach_state)
                mach_states = tuple(mach_states)

                if not arriving_job:
                    state = (0, mach_states)
                else:
                    state = (arriving_job.duration, mach_states)

                # Obtain action
                action = scheduler.evaluate(state)
                type = action[0]
                mach_idx = action[1]
                if type == 1:
                    self.machines[mach_idx].load_job(arriving_job)

                # Update environment state
                machine.update_state()
                time += 1

            # Sum rewards from machines
            total_reward = 0
            for machine in self.machines:
                total_reward += machine.reward
            rewards.append(total_reward)

        return rewards
