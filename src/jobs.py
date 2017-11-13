import numpy as np

import pdb

class Jobs(list):
    def __init__(self, dist_name, dist_params):
        super().__init__()

        self.dist_name = dist_name
        self.dist_params = dist_params

    @staticmethod
    def save_to_file(jobs, file_name):
        params_str = ["\t%s: %s" % (key, value) \
                            for key, value in jobs.dist_params.items()]
        params_str = "\n".join(params_str)

        header_str = [
            "Distribution type: " + jobs.dist_name,
            "Distribution params:",
            params_str,
        ]
        header_str = "\n".join(header_str) + "\n"

        data = np.array([Job.serialize(job) for job in jobs])
        np.savetxt(file_name, data, fmt="%d", header=header_str)

    @staticmethod
    def read_from_file(file_name):
        data = np.loadtxt(file_name)

class Job():
    def __init__(self, arrival, duration, value, index):
        self.arrival = arrival
        self.duration = duration
        self.value = value
        self.index = index

    @staticmethod
    def deserialize(data):
        return Job(**data)

    @staticmethod
    def serialize(job):
        return np.array([job.arrival, job.duration, job.value, job.index])
