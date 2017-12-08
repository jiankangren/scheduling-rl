import logging
    
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
        self.work_end_time = -1
        self.total_reward = 0

    def load_jobs(self, job):
        if (self.mode == "non-premptive" and self.current_job == None) or \
                self.mode == "premptive":
            self.current_job = job

            self.work_start_time = job.arrival
            self.work_end_time = job.departure

            if __debug__:
                log_str = "Machine %d scheduled job %d at time %d" % (self.mach_idx,
                        self.job.index, self.work_start_time)
                logger.debug(log_str)
            return True
        else:
            if __debug__:
                log_str = "Machine %d unable to schedule job %d at time %d" % \
                    (self.mach_idx, self.job.index, self.job.arrival)
            return False

    def is_idle(self):
        return (self.current_job == None)

    def unload_job(self):
        self.current_job = None

        self.work_start_time = -1
        self.work_end_time = -1

        self.total_value += self.current_job.value

        if __debug__:
            log_str = "Machine %d completed job %d at time %d" % (self.mach_idx,
                    self.job.index, self.work_end_time)
        
        return True

class State(list):
    def __init__(self, job_arrival, machines, time):
        super().__init__()

        mach_state = [[machine.current_job, machine.work_end_time - time] for
                machine in machines]
        self = [job_arrival, mach_state]


class Environment():
    def __init__(self, config, job_gen, save_path, load_jobs):
        self.job_gen = job_gen
        self.save_path = save_path

        #self.episodes = config["episodes"]
        #self.job_horizon = config["job_horizon"]
        self.mode = config["mode"]
        self.machines = [Machine(i, self.mode) for i in range(config["num_machines"])]
        
        # Obtain jobs
        """
        self.job_sequences = []
        generation_scheme = config["generation_scheme"]
        if not load_jobs:
            if generation_scheme == "single":
                jobs_sequence = job_gen.generate(self.job_horizon, save_path)
                self.job_sequences.append(job_sequence)
            elif generation_scheme == "multiple":
                for episode in range(self.episodes):
                    job_sequence = job_gen.generate(self.job_horizon, save_path)
                    self.job_sequences.append(job_sequence)
            else:
                raise ValueError("Unknown configuration parameter %s for \
                        'generation_scheme'" % (generation_scheme))
        else:
            print("Complete me")
        """

        # Save information
        
    def evaluate(self):
        pass

    def train(self):
        pass
