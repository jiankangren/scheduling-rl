import itertools, os, json, yaml
import numpy as np
from abc import ABC, abstractmethod

import pdb

class Job():
    def __init__(self, arrival, duration, value, index):
        self.arrival = arrival
        self.duration = duration
        self.departure = arrival + duration
        self.value = value
        self.index = index

    @staticmethod
    def deserialize(data_str):
        data = [int(x) for x in data_str.split() if x.isdigit()]
        return Job(*data)

    @staticmethod
    def serialize(job):
        return "%5d %5d %5d %5d" % (job.arrival, job.duration, job.value, job.index)

class Jobs(list):
    def __init__(self, config=None):
        super().__init__()
        
        self.config = config

    @staticmethod
    def save_to_file(jobs, file_path):
        header_str = [
            "### Configuration ###",
            yaml.dump(jobs.config, default_flow_style=False),
        ]
        header_str = "\n".join(header_str)

        data_str = ["### Data ###"] + [Job.serialize(job) for job in jobs]
        data_str = "\n".join(data_str)

        with open(file_path, "w") as file:
            file.write(header_str + "\n" + data_str)
        
    @staticmethod
    def load_from_file(file_path):
        with open(file_path, "r") as file:
            content = file.read()
        sections = list(filter(None, content.split("###")))
        
        # Parse configuration
        config = yaml.load(sections[1])
        jobs = Jobs(config)

        # Parse data
        data = list(filter(None, sections[3].split("\n")))
        jobs.extend([Job.deserialize(datum) for datum in data])

        return jobs
        
class JobGenerator(ABC):
    def __init__(self, config, data_path):
        self.dist_name = self.__class__.__name__
        
        self.train_path = os.path.join(data_path, "train")
        if not os.path.exists(self.train_path):
            os.makedirs(self.train_path)

        self.eval_path = os.path.join(data_path, "evaluate")
        if not os.path.exists(self.eval_path):
            os.makedirs(self.eval_path)
        
        self.config = config["job_generator"]
        self.dist_params = self.config["parameters"]
    
    @abstractmethod
    def generate_job_sequence(self, num_jobs=0):
        pass

    def generate_job_sequences(self, data_path, type):
        types = ["train", "evaluate"]
        save_paths = { "train": self.train_path, "evaluate": self.eval_path }

        if not type in types:
            raise ValueError("Invalid value for parameter 'type': %s" % (type))

        job_sequences = []
        job_data_path = save_paths[type]

        # Load job sequences if exists
        job_files = os.listdir(job_data_path)
        if len(job_files) > 0:
            for job_file in job_files:
                job_path = os.path.join(job_data_path, job_file)
                job_sequences.append(Jobs.load_from_file(job_path))

        # Create job sequences and save
        else:
            num_sequences = self.config[type]["num_sequences"]
            job_horizon = self.config[type]["job_horizon"]

            for i in range(num_sequences):
                num_files = JobGenerator.get_file_count(job_data_path)
                file_name = "%s_%d.txt" % (self.dist_name, num_files)
                file_path = os.path.join(job_data_path, file_name)
                job_sequences.append(self.generate_job_sequence(file_path,
                                                                job_horizon))

        # Modify job_sequences to be a cycle
        job_sequences = itertools.cycle(job_sequences)
        return job_sequences, num_sequences

    @staticmethod
    def get_file_count(dir):
        return len(os.listdir(dir))

class Uniform(JobGenerator):
    def __init__(self, config, data_path):
        super().__init__(config, data_path)
        
    def generate_job_sequence(self, file_path, num_jobs=0):
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

        Jobs.save_to_file(jobs, file_path)

        return jobs
