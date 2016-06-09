#! /usr/bin/env bash

if [ $# -gt 0 ]; then
  echo "Aggregating sensor data from" $1 "to give subsessions, work sessions, quartiles of edits-per-launch, and the time_spent on each project by a student..."

  ./subsessions.py $1 subsessions.csv
  ./work_sessions.py subsessions.csv work_sessions.csv
  ./quartiles.py subsessions.csv quartiles.csv
  ./time_spent.py work_sessions.csv time_spent.csv
else
  echo "Usage: ./aggregate.sh [filename]"
fi
