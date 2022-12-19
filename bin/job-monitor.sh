#!/bin/bash
# MIT License
#
# Copyright (c) 2022 Simo Tuomisto, Aalto Scientific Computing
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


if [ -z ${SLURM_JOB_ID+x} ] ; then
  echo "Could not get \$SLURM_JOB_ID. Will not start the monitoring."
else

  start_monitoring(){
      # Defaults
      export JOB_MONITOR_GATHER_INTERVAL=${JOB_MONITOR_GATHER_INTERVAL:-"10s"}
      export JOB_MONITOR_FLUSH_INTERVAL=${JOB_MONITOR_FLUSH_INTERVAL:-"60s"}
      export JOB_MONITOR_AVERAGE_INTERVAL=${JOB_MONITOR_AVERAGE_INTERVAL:-"60s"}
      MONITOR_PID_FILE=/tmp/job_monitor_${SLURM_JOB_ID}.pid
      if [ -z ${MONITOR_DEBUG_OUTPUT+x} ] ; then
          MONITOR_OUTPUT_FILE=/dev/null
      else
          MONITOR_OUTPUT_FILE=job_monitor_${SLURM_JOB_ID}.out
      fi
      if [ ! -z ${CUDA_VISIBLE_DEVICES+x} ] ; then
          export TELEGRAF_CONFIG_PATH=${JOB_MONITOR_CONFIG_DIR}/job-monitor-cuda.conf
      elif [ ! -z ${ROCR_VISIBLE_DEVICES+x} ] ; then
          export TELEGRAF_CONFIG_PATH=${JOB_MONITOR_CONFIG_DIR}/job-monitor-rocm.conf
      else
          export TELEGRAF_CONFIG_PATH=${JOB_MONITOR_CONFIG_DIR}/job-monitor-cpu.conf
      fi
      #export MONITOR_CGROUP=/sys/fs/cgroup/cpuset/slurm/uid_${UID}/job_${SLURM_JOB_ID}/step_batch/
      export MONITOR_CGROUP="/sys/fs/cgroup/cpuset/slurm/uid_${UID}/job_${SLURM_JOB_ID}/step_*"
      export MONITOR_METRICS_FILE=metrics_${SLURM_JOB_ID}.json
      telegraf &> ${MONITOR_OUTPUT_FILE} &
      echo "$!" > ${MONITOR_PID_FILE}
      echo "Monitoring started. Monitor process ID is stored in ${MONITOR_PID_FILE}"
  }

  stop_monitoring(){
      MONITOR_PID_FILE=/tmp/job_monitor_${SLURM_JOB_ID}.pid
      if [ -z ${MONITOR_DEBUG_OUTPUT+x} ] ; then
          MONITOR_OUTPUT_FILE=/dev/null
      else
          MONITOR_OUTPUT_FILE=job_monitor_${SLURM_JOB_ID}.out
      fi
      if [ -f ${MONITOR_PID_FILE} ]; then
          cat ${MONITOR_PID_FILE} | xargs kill >> ${MONITOR_OUTPUT_FILE} 2>&1
          echo 'Monitoring stopped.'
          rm ${MONITOR_PID_FILE}
      fi
  }

  # Start monitoring
  start_monitoring

  # Set stopping conditions for monitoring
  trap stop_monitoring TERM EXIT
fi
