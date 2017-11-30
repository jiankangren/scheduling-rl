import os
import numpy as np
from abc import ABC, abstractmethod
from jobs import Job, Jobs

import pdb

class JobGenerator(ABC):
    def __init__(self, config, data_path):
        self.dist_name = self.__class__.__name__
        self.save_path = os.path.join(data_path, self.dist_name)
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.config = config
        self.dist_params = config["parameters"]
    
    @abstractmethod
    def generate(self, num_jobs=0):
        pass

    def get_file_count(self):
        files = os.listdir(self.save_path)
        return len(files)

class Uniform(JobGenerator):
    def __init__(self, config, data_path):
        super().__init__(config, data_path)
        
    def generate(self, num_jobs=0, file_path=None):
        # Arrivals
        time = 0
        arrivals = []
        while len(arrivals) < num_jobs:
            if np.random.random() < self.dist_params["new"]:
                arrivals.append(time)
            time += 1

        # Duration
        durations = np.random.randint(low=self.dist_params["low"],
                                      high=self.dist_params["high"] + 1, 
                                      size=num_jobs)
        # Value
        func = eval(self.dist_params["func"])
        values = func(durations)
        
        # Jobs
        jobs = Jobs(self.config)
        jobs.extend([Job(arrivals[i], durations[i], 
                         values[i], i) for i in range(num_jobs)])

        # Save job sequence
        if file_path:
            Jobs.save_to_file(jobs, file_path)
        else:
            count = str(self.get_file_count())
            file_name = self.dist_name + "_" + count + ".txt"
            file_path = os.path.join(self.save_path, file_name)
            Jobs.save_to_file(jobs, file_path)

        return jobs
