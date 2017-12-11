import getopt, os, sys, time, yaml
from environment import Environment
from jobs import Jobs
from job_generator import Uniform
from schedulers import *

import pdb

# Constants
job_gen_map = {
    "uniform": Uniform,
}

sched_map = {
    "value iteration": SchedulerValueIteration,
}


def parse_configuration(config_path):
    try:
        with open(config_path, "r") as config_file:
            config_yaml = config_file.read()
    except:
        raise EnvironmentError("Unable to open %s" % (config_path))

    return yaml.load(config_yaml)

def print_usage_info():
    print("Complete me")

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
    # TODO Change directory to work_path
    config_path = None
    directory = None
    load_jobs = False
    evaluate = False
    train = False

    try:
        short_flags = "hc:d:et"
        long_flags = ["help", "config=", "directory=", "evaluate", "train"]
        opts, args = getopt.getopt(sys.argv[1:], short_flags, long_flags)
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
        elif opt in ("-e", "--evaluate"):
            evaluate = True
        elif opt in ("-t", "--train"):
            train = True 
        else:
            raise ValueError("Unknown (opt, arg): (%s, %s)" % (opt, arg))

    # Directory and configuration options
    if directory and not config_path:
        config_path = os.join.path(directory, "configuration.yaml")
        if not os.path.exists(config_path):
            raise EnvironmentError("Unable to locate %s" % (config_path))
        save_path = directory
    elif directory and config_path:
        save_path = directory
    elif not directory and config_path:
        save_dir_name = time.strftime("%y:%m:%d:%H:%M:%S")
        save_path = os.path.join(data_path, save_dir_name)
        os.makedirs(save_path)
    else:
        print_usage_info()
        sys.exit()

    # Parse configuration
    config = parse_configuration(config_path)
    
    # Job generator
    job_gen_name = config["job_generator"]["name"]
    job_gen = job_gen_map[job_gen_name](config, save_path)

    # FIXME continue work from here
    # Schedulers
    sched_algo = config["scheduler"]["algorithm"]
    scheduler = sched_map[sched_algo](config, job_gen, save_path)

    scheduler_optimal = SchedulerOptimal()

    # Environment
    environment = Environment(config, job_gen, save_path, load_jobs)


    # FIXME this will depend if it is offline or online
    # FIXME the train_sequences will have to be a Python generator
    if train:
        train_sequences = None
        if config["common"]["train_mode"] == "online":
            train_sequences = job_gen.generate_job_sequences(save_path, "train")

        scheduler.train(train_sequences)

    # FIXME need to be able to load a Q_func in the future
    # I should pass in the scheduler itself rather than the Q_func along which
    # will have to be evaluated
    if evaluate:
        # Evaluate scheduler
        eval_sequences = job_gen.generate_job_sequences(save_path, "evaluate")
        environment.simulate(eval_sequences, 1, scheduler)

        # Evaluate optimal scheduler
        num_machines = config["environment"]["num_machines"]
        opt_schedule = scheduler_optimal.evaluate(eval_sequences, 1)

if __name__ == "__main__":
    main()
