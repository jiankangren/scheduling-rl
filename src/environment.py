import logging
    
# TODO move this to main under __debug__
logger = logging.getLogger("Env-Logger")
hdlr = logging.FileHandler("../logs")
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

class Environment():
    def __init__(self, config, directory=None):
        if config_path:
            self._parse_configuration(config)

        # Environment subconfiguration
        env_config = config["environment"]
        self.num

        # Job generaton subconfiguration

    def _parse_configuration(self, config):
        """
        try:
            with open(config_path, "r") as config_file:
                config_yaml = config_file.read()
        except:
            raise EnvironmentError("Unable to open %s" % (config_path))

        cfg = yaml.load(config_yaml)
        """

        # Environment subconfiguration
        env_cfg = config["environment"]
        self.machines = [Machine() for i in range(env_cfg["num_machines"])]
        self.episodes = env_cfg["episodes"]




