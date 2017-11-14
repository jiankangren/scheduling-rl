import getopt, os, sys, yaml
from jobs import Jobs
from job_generator import SchemePUS
from schedulers.sched_optimal import SchedOptimal

# Constants
low = 1
high = 5
num_jobs = 10
func = "lambda x: x * x"

job_generator_map = {
    "SchemePUS": SchemePUS,
}

def _parse_configuration(config_yaml):
    try:
        with open(config_yaml, "r") as config_file:
            config = config_file.read()
    except:
        raise EnvironmentError("Unable to open %s" % (config_yaml))

    return yaml.load(config)

def main():
    # Initialize directories
    src_path = os.path.abspath(os.path.dirname(__file__))
    base_path = os.path.abspath(os.path.join(src_path, os.pardir))
    
    data_path = os.path.join(base_path, "data")
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    # Parse arguments
    config_yaml = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:s:", 
                                   ["help", "config", "sequence"])
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
            config_yaml = arg
        elif opt in ("-s", "--sequence"):
            jobs = Jobs.read_from_file(arg)
        else:
            raise ValueError("Unknown (opt, arg): (%s, %s)" % (opt, arg))

    # Parse configuration
    if config_yaml:
        config = _parse_configuration(config_yaml)
        job_gen = job_generator_map[config["name"]](config, data_path)
        jobs = job_gen.generate(num_jobs)

    # Run scheduler on jobs
    sched_optimal = SchedOptimal()
    opt_schedule = sched_optimal.schedule(jobs, 1)

if __name__ == "__main__":
    main()
