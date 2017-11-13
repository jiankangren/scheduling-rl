import numpy as np
from abc import ABC, abstractmethod
from jobs import Job, Jobs

import pdb

class JobGenerator(ABC):
    def __init__(self):
        self.dist_name = None
        self.dist_params = {}
    
    @abstractmethod
    def generate(self, num_jobs=0):
        pass

# TODO create configuration files and just pass in a params
class SchemePUS(JobGenerator):
    #def __init__(self, low, high, func=None):
    def __init__(self, params):
        super().__init__()

        self.dist_name = self.__class__.__name__
        self.dist_params = params

        """
        self.dist_params = {
            "low": low,
            "high": high,
            "func": func
        }
        """

    # GE how should arrivals be modeled
    def generate(self, num_jobs=0, file_name=None):
        # Arrivals
        time = 0
        arrivals = []
        while len(arrivals) < num_jobs:
            if np.random.randint(2) == 1:
                arrivals.append(time)
            time += 1

        # Duration
        durations = np.random.randint(low=self.dist_params["low"],
                                      high=self.dist_params["high"], 
                                      size=num_jobs)
        # Value
        func = eval(self.dist_params["func"])
        values = func(durations)
        
        # Jobs
        jobs = Jobs(self.dist_name, self.dist_params)
        jobs.extend([Job(arrivals[i], durations[i], 
                         values[i], i) for i in range(num_jobs)])

        # Save job sequence
        if not file_name == None:
            Jobs.save_to_file(jobs, file_name)

        return jobs
