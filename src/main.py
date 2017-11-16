import getopt, os, sys, time, yaml
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
    load_jobs = False

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
            load_jobs = True
        else:
            raise ValueError("Unknown (opt, arg): (%s, %s)" % (opt, arg))

    # Check if directory
    if directory:
        config_path = os.join.path(directory, "configuration.yaml")
        if not os.path.exists(config_path):
            raise EnvironmentError("Unable to locate %s" % (config_path))

    # Parse configuration
    config = _parse_configuration(config_path)
    job_gen_config = config["job_generator"]
    agent_config = config["agent"]
    env_config = config["environment"]

    # Save configuration
    if not directory:
        save_dir_name = time.strftime("%y:%m:%d:%H:%M:%S")
        save_path = os.path.join(data_path, run_dir_name)
        os.makedirs(save_path)

    # FIXME data_path part isn't correct
    job_gen = job_generator_map[job_gen_config["name"]](job_gen_config,
            save_path)
    agent = agent_map["type"](agent_config, job_gen, save_path)
    env = Environment(env_config, job_gen, save_path, load_jobs)

    


    """
    # Run scheduler on jobs
    sched_optimal = SchedOptimal()
    opt_schedule = sched_optimal.schedule(jobs, 1)
    """

if __name__ == "__main__":
    main()
