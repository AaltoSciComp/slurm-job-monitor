#!/usr/bin/env python
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as mpl
import click

def normalize_metrics(hardware, data):

    if hardware in ('cpu', 'gpu'):
       return data / 100
    elif hardware == "ram":
       return data / (1024*1024)
    elif hardware == "vram":
       return data / 1024

    return data


def plot_metrics(metrics_df, job_id=None, process=None, view=False, save=True):

    mpl.style.use("default")

    ylabels = {
      "cpu": "CPU utilization",
      "ram": "MB of RAM in use",
      "gpu": "GPU utilization",
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

        if hardware in ('cpu', 'gpu'):
            ax.axhline(y=1, linestyle='-.', color='k', label=f"Single {hardware.upper()} fully utilized")
            mpl.legend()

        if save:
            savename = f"{hardware}_usage_{job_id}"
            if len(process) > 0:
                savename = f"{savename}_{process}"
            mpl.savefig(f"{savename}.png")

    if view:
        mpl.show()


def read_metrics(metrics):

    try:
        with open(metrics,"r") as f:
            lines = f.readlines()

        jsons = []
        for line in lines:
            job_id = int(json.loads(line)["tags"]["job_id"])
            try:
                process = json.loads(line)["tags"]["process_name"]
            except Exception as e:
                process = ""
            df = pd.read_json(line, dtype=True)
            df["jobid"] = job_id
            df["process"] = process
            jsons.append(df)
    except Exception as e:
        print(f"Encountered a problem reading file {metrics}.")
        raise e

    metrics_df = pd.concat(jsons).reset_index()

    metrics_df.drop(["tags", "name"], axis=1, inplace=True)

    metrics_df.rename(columns={
                 "timestamp" : "Time",
                 "index": "Metric",
                 "fields": "Value",
               },
               inplace=True)

    metrics_df["Hardware"] = metrics_df["Metric"].apply(lambda x: x.split("_")[0])
    metrics_df.dropna(inplace=True)

    return metrics_df

def export_metrics(metrics_df, job_id=None, process=None):

    export_df = metrics_df.reset_index()
    export_df = export_df.pivot(index='Time', columns='Metric', values='Value')
    export_df.index.rename('time', inplace=True)
    savename = f"metrics_{job_id}"
    if len(process) > 0:
        savename = f"{savename}_{process}"
    export_df.to_csv(f"{savename}.csv")

@click.command()
@click.option("-n", "--no-save", is_flag=True, default=False, help="Do not save figures (default: False)")
@click.option("-e", "--export", is_flag=True, default=False, help="Export data in CSV (default: False)")
@click.option("--view / --no-view", default=False, help="View figures (default: False)")
@click.argument("metrics")

def main(metrics, no_save=True, view=False, export=False):
    metrics_df = read_metrics(metrics)
    for grouping, data in metrics_df.groupby(["jobid", "process"]):
        job_id = grouping[0]
        process = grouping[1]
        if view or not no_save:
            plot_metrics(data, job_id=job_id, process=process, view=view, save=not no_save)
        if export:
            export_metrics(data, job_id=job_id, process=process)


if __name__=="__main__":
    main()
