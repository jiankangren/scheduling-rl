import getopt, os, sys, yaml
from jobs import Jobs
from job_generator import Uniform
from schedulers.sched_optimal import SchedOptimal

# Constants
low = 1
high = 5
num_jobs = 10
func = "lambda x: x * x"

job_generator_map = {
    "Uniform": Uniform,
}

def _parse_configuration(config_path):
    try:
        with open(config_path, "r") as config_file:
            config_yaml = config_file.read()
    except:
        raise EnvironmentError("Unable to open %s" % (config_path))

    return yaml.load(config_yaml)

def main():
    # Initialize directories
    src_path = os.path.abspath(os.path.dirname(__file__))
    base_path = os.path.abspath(os.path.join(src_path, os.pardir))
    
    data_path = os.path.join(base_path, "data")
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    logs_path = os.path.join(base_path, "logs")
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    # Parse arguments
    config_path = None
    directory = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:d:", 
                                   ["help", "config", "directory"])
    except getopt.GetoptError as err:
        print(err)
        print_usage_info()
        sys.exit(2)

    # Print help message 
    if len(opts) == 0:
        print_usage_info()
        sys.exit()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage_info()
            sys.exit()
        elif opt in ("-c", "--config"):
            config_path = arg
        elif opt in ("-s", "--directory"):
            directory = arg
        else:
            raise ValueError("Unknown (opt, arg): (%s, %s)" % (opt, arg))

    # Check if directory
    if directory:
        config_path = os.join.path(directory, "configuration.yaml")
        if not os.path.exists(config_path):
            raise EnvironmentError("Unable to locate %s" % (config_path))

    # Parse configuration
    config = _parse_configuration(config_path)
    
    agent_config = config["agent"]
    agent = agent_map["type"](agent_config)

    env_config = config["environment"]
    if not directory:
        job_gen_config = config["job_generator"]
        job_gen = job_generator_map[job_gen_config["name"]](config, data_path)
        env = Environment(env_config, job_gen=job_gen)
    else:
        env = Environment(env_config, dir_path=directory)

    """
    # Run scheduler on jobs
    sched_optimal = SchedOptimal()
    opt_schedule = sched_optimal.schedule(jobs, 1)
    """

if __name__ == "__main__":
    main()
