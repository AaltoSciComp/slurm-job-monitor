#!/bin/bash -l
#SBATCH --time=00:15:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=6
#SBATCH --output=test-job-monitor-cpu.out


## Starting monitoring

module use ../modules

module load job-monitor

# Enable debugging output
#export MONITOR_DEBUG_OUTPUT=y

source job-monitor.sh

## Program code

[[ ! -d examples ]] && git clone https://github.com/pytorch/examples.git

# Load extra modules
[[ $# -gt 0 ]] && module load ${@:1}

module list

env > job-monitor-cpu-env.out

cd examples/mnist

time srun python main.py --epochs=20
