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

        # Generate all states, transitions, and rewards for offline
        train_mode = config["common"]["train_mode"]
        if train_mode == "offline":
            dist_params = config["job_generator"]["parameters"]
            self.generate_state_space(config, dist_params, num_machines)

    def _get_next_states(type, state, action, all_state, job_arrivals):
        pass

    # FIXME only works with Uniform for now
    def generate_state_space(self, config, dist_params, num_machines):
        # Obtain distribution parameters
        new_prob = dist_params["new"]
        low = dist_params["low"]
        high = dist_params["high"]

        job_types = [0] + [i for i in range(low, high+1)]

        # Compute probabilites
        probabilites = {}
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
            for rem_time in range(job_type-2, 0, 1):
                mach_state = (job_type, rem_time)
                inter_mach_states.append(mach_states)

        # Determine scheduled machine states
        sched_mach_states = []
        for job_type in job_types[1:]:
            mach_state = (job_type, job_type-1)
            sched_mach_states.append(mach_states)

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
        permute_nop_states = list(product(inter_states, repeat=num_machines))


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
        

    # FIXME simulation will have to be different for training/evaluating
    # FIXME need to iterate through all job_sequences, currently this is only
    # happening for a single one
    def simulate(self, job_sequences, episodes, scheduler):
        # Iterate through all episodes
        for episode in range(episodes):
            time = 0
            job_idx = 0
            job_sequence = next(job_sequences)

            # Iterate through a job sequence
            while job_idx < len(job_sequence):
                arriving_job = job_sequence[job_idx]
                if arriving_job.arrival == time:
                    job_idx += 1
                else:
                    arriving_job = None
                
                # FIXME only for a single machine for now
                # Obtain state
                machine = self.machines[0]
                machine_state = machine.get_state()

                if not arriving_job:
                    state = (0, machine_state)
                else:
                    state = (arriving_job.duration, machine_state)

                # Obtain action
                action = scheduler.evaluate(state)
                if action == 1:
                    machine.load_job(arriving_job)

                # Update environment state
                machine.update_state()
                time += 1

            # Sum rewards from machines
            total_reward = 0
            for machine in self.machines:
                total_reward += machine.reward

            print(total_reward)

