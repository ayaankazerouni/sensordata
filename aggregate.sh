#! /usr/bin/env bash

if [ $# -gt 0 ]; then
  echo "Aggregating sensor data from" $1 "to give subsessions, 
  work sessions, and the time_spent on each project by a student."

  mkdir -p results

  ./subsessions.py $1 ./results/subsessions.csv
  ./work_sessions.py ./results/subsessions.csv ./results/work_sessions.csv
  ./time_spent.py ./results/work_sessions.csv ./results/time_spent.csv
  ./launch_stats.py quartiles ./results/subsessions.csv ./results/launch_quartiles.csv
  ./launch_stats.py totals ./results/work_sessions.csv ./results/launch_totals.csv
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
