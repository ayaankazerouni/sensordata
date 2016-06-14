#! /usr/bin/env bash

if [ $# -gt 0 ]; then
  echo "Aggregating sensor data from" $1 "to give subsessions, work sessions, and the time_spent on each project by a student."

  ./subsessions.py $1 subsessions.csv
  ./work_sessions.py subsessions.csv work_sessions.csv
  ./time_spent.py work_sessions.csv time_spent.csv
else
  echo "Does a complete aggregation of sensordata in the provided sensordata file, by running the following processes:
    ./subsessions.py [sensordatafile] {generates subsessions.csv}
    ./work_sessions.py subsessions.csv work_sessions.csv {generates work_sessions.csv}
    ./time_spent.py work_sessions.csv time_spent.csv  {generates time_spent.csv}"
  echo "After execution, you will have information about subsession data, work_session data, the time spent on each\
  project, and the number of edits-per-launch organised into quartiles."
  echo "Usage: ./aggregate.sh [filename]"
fi
