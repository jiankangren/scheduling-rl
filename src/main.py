import getopt, yaml, sys
from job_generator import SchemePUS

# Constants
low = 1
high = 5
num_jobs = 10
func = "lambda x: x * x"

def parse_configuration(config_yaml):
    try:
        with open(config_yaml, "r") as config_file:
            config = config_file.read()
    except:
        raise EnvironmentError("Unable to open %s" % (config_yaml))

    return yaml.load(config)

def main():
    # Parse arguments
    config_file = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help", "config"])
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
        else:
            raise ValueError("Unknown (opt, arg): (%s, %s)" % (opt, arg))

    # Parse configuration
    config = parse_configuration(config_yaml)

    job_gen = SchemePUS(1, 5, func)
    job_gen.generate(num_jobs, "../data/scheme-pus/data.txt")

if __name__ == "__main__":
    main()
