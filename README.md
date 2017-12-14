# Scheduling RL
A simulation environment for running reinforcement learning algorthms for online
stochastic scheduling. 

The simulator can be run as follows:
```
python3 main.py [--options]
```

where options are specified as follows:
* -h, --help        prints out usage information
* -c, --config=     path to YAML configuration file
* -e, --evaluate    evaluates learned policies against an optimal offline scheduler
* -t, --train       trains a policy according to configuration parameters

When either the 'train' or 'evaluate' options are specified, the program will
generate a eponymous directory containing all job sequences.

Additionally, to run an existing example, simply run:
```
./run_example.sh
```

## Configuration File
The simulator takes in a single YAML configuration file. An example of such a
configuration file is outlined below:

```
common:
    schedule_mode: ["preemptive", "non-preemptive"]
    train_mode: ["offline", "online"]

schedule:
    algorithm: ["value iteration"]
    function: ["table"]

environment:
    episodes: (unsigned int)
    num_machines: (unsigned int)

job_generator:
    name: ["uniform"]
    train:
        job_horizon: (unsigned int)
        num_sequences: (unsigned int)
    evaluate:
        job_horizon: (unsigned int)
        num_sequences: (unsigned int)
    parameters:
        func: "lambda x: <value function>"
        [other parameters]
```

Keywords in brackets represent the current set of options available to choose
from for a particular configuration parameter. The "func" parameter has to be a
lambda function that can be assigned to anything. A job generator currently
models only a uniform distribution but it will be able to model others as well
and each distribution will have corresponding parameter options under the
"parameters" parameter.
