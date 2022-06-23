# slurm-job-monitor

This tool uses telegraf, cgroups and nvidia-smi to monitor
CPU, RAM, GPU and GPU VRAM utilization during Slurm job's
runtime.

## Requirements

This tool requires telegraf to be installed.

Visualization requires Python 3 with pandas, matplotlib and click.

## Usage

Include the following in your sbatch-script:

```sh
module use /path/to/slurm-job-monitor/modules
module load job-monitor/0.1

source job-monitor.sh
```

## Visualization

```sh
module use /path/to/slurm-job-monitor/modules
module load job-monitor/0.1

job-monitor-visualize.py metrics_5582199.json          # For saved .png figures
job-monitor-visualize.py --view metrics_5582199.json   # For viewing the images as well
job-monitor-visualize.py --export metrics_5582199.json # For storing the data as a .csv file
```

For all options, see:
```sh
job-monitor-visualize.py --help
```

Visualization does not currently work for multiple GPUs.
