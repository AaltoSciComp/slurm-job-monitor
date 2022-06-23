# slurm-job-monitor

This tool uses telegraf, cgroups and nvidia-smi to monitor
CPU, RAM, GPU and GPU VRAM utilization during Slurm job's
runtime.

## Requirements

This tool requires telegraf to be installed.

## Usage


```sh
module use modules
module load job-monitor/0.1

source job-monitor.sh
```
