import json, yaml

import pdb

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
    def read_from_file(file_path):
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
