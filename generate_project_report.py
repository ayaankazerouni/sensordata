#! /usr/bin/env python3 

"""Generate a "report" of incremental development metrics from raw sensordata
for an assignment. Includes ids for student-projects along with results
for all the different measures.

To use:
    ./generate_project_report.py -h 
"""

import argparse
import os
import sys
import pandas as pd

# import sensordata pipeline methods
from subsessions import get_subsessions
from work_sessions_from_subsessions import get_work_sessions
from time_spent import get_time_spent
from early_often import earlyoften
from consolidate_sensordata import consolidate_student_data

# method to do stuff
def aggregate(args):
    # ask for information up front, if needed 
    if args.yes:
        threshold = 3
        path_repo_mining = 'data/repo-mining.csv'
    else:
        threshold = input('Please enter a threshold in hours for work_sessions (leave blank for default):')
        try:
            threshold = int(float(threshold))
        except ValueError:
            print('Invalid input. Using default value of 3 hours.')
            threshold = 3
        path_repo_mining = input('Please enter a path to CSV output from repository mining (leave blank for default)')
        if len(path_repo_mining) == 0:
            path_repo_mining = 'data/repo-mining.csv'
    
    path_subsessions = os.path.join(args.output, 'subsessions.csv')
    get_subsessions(args.raw, path_subsessions, threshold=threshold)
    path_worksessions = os.path.join(args.output, 'worksessions.csv')
    get_work_sessions(path_subsessions, path_worksessions)
    path_timespent = os.path.join(args.output, 'timespent.csv')
    get_time_spent(path_worksessions, path_timespent)
    path_earlyoften = os.path.join(args.output, 'earlyoften.csv')
    earlyoften(args.raw, outfile=path_earlyoften, submissionspath=args.submissions)
    report = consolidate_student_data(webcat_path=args.submissions,
        raw_inc_path=args.raw,
        time_path=path_timespent,
        ws_path=path_worksessions,
        repo_mining_path=path_repo_mining)
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('raw',
        help='path to raw sensordata for multiple students working on a single assignment')
    parser.add_argument('submissions',
        help='path to web-cat submission for students represented in the sensordata')
    parser.add_argument('--output', '-o',
        help='path to an empty output directory, created if needed',
        default='./results')
    parser.add_argument('--yes', '-y',
        help='use default values where appropriate',
        action='store_const',
        const=True)
    args = parser.parse_args()


    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    if os.listdir(args.output) == []:
        df = aggregate(args) # play with consolidated data here
        df.to_csv(os.path.join(args.output, 'consolidated.csv'), index=True)
    else:
        sys.exit('\nError: Please make sure your output directory is empty.')
