#! /usr/bin/env bash

if [ $# -gt 0 ]; then
  echo "Aggregating sensor data from" $1 "to give subsessions,
  work sessions, and the time_spent on each project by a student."

  mkdir -p results

  if [ ! -f './results/subsessions.csv' ]; then
    ./subsessions.py $1 ./results/subsessions.csv
  fi
  if [ ! -f './results/work_sessions.csv' ]; then
    ./work_sessions.py ./results/subsessions.csv ./results/work_sessions.csv
  fi
  if [ ! -f './results/time_spent.csv' ]; then
    ./time_spent.py ./results/work_sessions.csv ./results/time_spent.csv
  fi
  if [ ! -f './results/subsession_summaries.csv' ]; then
    ./stats.py summary ./results/subsessions.csv ./results/subsession_summaries.csv
  fi
  if [ ! -f './results/launch_totals.csv' ]; then
    ./stats.py launch_totals ./results/work_sessions.csv ./results/launch_totals.csv
  fi
else
  echo "Does a complete aggregation of sensordata in
  the provided sensordata file, by running the following processes:
    ./subsessions.py <sensordatafile> {generates subsessions.csv}
    ./work_sessions.py subsessions.csv work_sessions.csv {generates work_sessions.csv}
    ./time_spent.py work_sessions.csv time_spent.csv  {generates time_spent.csv}"
  echo "After execution, you will have information about subsession data, work_session data,
  and the time spent on each project."
  echo "Usage: ./aggregate.sh [filename]"
fi
