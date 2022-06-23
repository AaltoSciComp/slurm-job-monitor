#!/usr/bin/env python
import json
import pandas as pd
import matplotlib.pyplot as mpl
import click

def normalize_metrics(hardware, data):

    if hardware == "cpu":
       return data / 100
    elif hardware == "ram":
       return data / (1024*1024)
    elif hardware == "gpu":
       return data / 100
    elif hardware == "vram":
       return data / 1024

    return data


def plot_metrics(metrics_df, job_id=None, gpu_plots=False, view=False, save=True):

    mpl.style.use("default")

    ylabels = {
      "cpu": "Number of CPUs in use",
      "ram": "MB of RAM in use",
      "gpu": "Number of GPUs in use",
      "vram": "MB of VRAM in use",
    }

    measurements = ["max", "mean", "min"]

    for hardware, metric_hardware_df in metrics_df.groupby("Hardware"):

        metric_hardware_df = metric_hardware_df.pivot(index="Time", columns="Metric", values="Value")

        name_dict = { f"{hardware}_usage_{measurement}":f"{measurement.capitalize()} {hardware.upper()} usage"
            for measurement in measurements
        }

        metric_hardware_df.rename(columns=name_dict, inplace=True)

        metric_hardware_df = normalize_metrics(hardware, metric_hardware_df)

        fig = mpl.figure()
        ax = fig.gca()
        plot_columns = [
            f"{measurement.capitalize()} {hardware.upper()} usage"
            for measurement in measurements
        ]
        plot_styles = [":", "o-", ":"]
        metric_hardware_df.plot(
            y=plot_columns,
            ax=ax,
            style=plot_styles,
            title=f"{hardware.upper()} usage for job {job_id}",
            ylabel=ylabels[hardware])

        if save:
            mpl.savefig(f"{hardware}_usage_{job_id}.png")

    if view:
        mpl.show()


def read_metrics(metrics):

    try:
        with open(metrics,"r") as f:
            lines = f.readlines()
        job_id = int(json.loads(lines[0])["tags"]["job_id"])

        jsons = []
        for line in lines:
            jsons.append(pd.read_json(line, dtype=True))
    except Exception as e:
        print(f"Encountered a problem reading file {metrics}.")
        raise e

    metrics_df = pd.concat(jsons).reset_index()

    gpu_data = (metrics_df["name"] == "gpu_utilization").shape[0] > 0

    metrics_df.drop(["tags", "name"], axis=1, inplace=True)

    metrics_df.rename(columns={
                 "timestamp" : "Time",
                 "index": "Metric",
                 "fields": "Value",
               },
               inplace=True)

    metrics_df["Hardware"] = metrics_df["Metric"].apply(lambda x: x.split("_")[0])
    metrics_df.dropna(inplace=True)

    return metrics_df, job_id, gpu_data

def export_metrics(metrics_df, job_id=None):

    export_df = metrics_df.reset_index()
    export_df = export_df.pivot(index='Time', columns='Metric', values='Value')
    export_df.to_csv(f"metrics_{job_id}.csv")

@click.command()
@click.option("-n", "--no-save", is_flag=True, default=False, help="Do not save figures (default: False)")
@click.option("-e", "--export", is_flag=True, default=False, help="Export data in CSV (default: False)")
@click.option("--view / --no-view", default=False, help="View figures (default: False)")
@click.argument("metrics")

def main(metrics, no_save=True, view=False, export=False):
    metrics_df, job_id, gpu_data = read_metrics(metrics)
    if view or not no_save:
        plot_metrics(metrics_df, job_id=job_id, gpu_plots=gpu_data, view=view, save=not no_save)
    if export:
        export_metrics(metrics_df, job_id=job_id)


if __name__=="__main__":
    main()
