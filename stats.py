#! /usr/bin/env python3

import csv
import numpy as np
import sys

def subsession_summaries(infile, outfile, granularity=None):
    """
    Splits a subsession data file into quartiles based on edits sizes
    (statements) per subsession. Results are presented for each project
    as a whole or for each work_session within each project.

    The data generated here is on a per-student basis.

    Keyword arguments:
    infile      -- the name of the file containing subsession data
    outfile     -- the name of the file in which to put quartile data
    granularity -- 'WS' (or any non-None value) if you want work session level granularity
    """
    print('Getting subsession summary data...')
    fieldnames = [
        'userId',
        'projectId',
        'workSessionId',
        'assignment',
        'min',
        'q1',
        'q2',
        'q3',
        'max',
        'mean',
        's',
        'n'
    ]

    edit_sizes_stmts = []
    prev_row = None

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        for row in reader:
            prev_row = prev_row or row
            split_condition = row['projectId'] == prev_row['projectId'] \
                and row['userId'] == prev_row['userId']
            if (granularity != None):
                split_condition = split_condition and row['workSessionId'] == prev_row['workSessionId']

            if (split_condition):
                edit_size_stmts = int(row['editSizeStmts']) + int(row['testEditSizeStmts'])
                edit_sizes_stmts.append(edit_size_stmts)

                prev_row = row
            else:
                prev_ws = int(prev_row['workSessionId'])
                a = np.array(edit_sizes_stmts)
                low = np.percentile(a, 0)
                q1 = np.percentile(a, 25)
                median = np.percentile(a, 50)
                q3 = np.percentile(a, 75)
                high = np.percentile(a, 100)
                mean = np.mean(a)
                s = np.std(a)
                n = len(a)
                writer.writerow({'userId': prev_row['userId'], 'projectId': prev_row['projectId'], \
                    'workSessionId': prev_ws, 'assignment': prev_row['cleaned_assignment'], \
                    'min': low, 'q1': q1, 'q2': median, 'q3': q3, 'max': high, 'mean': mean, \
                    's': s, 'n': n })

                edit_sizes_stmts = []
                edit_size_stmts = int(row['editSizeStmts']) + int(row['testEditSizeStmts'])
                edit_sizes_stmts.append(edit_size_stmts)
                prev_row = row

        prev_ws = int(prev_row['workSessionId'])
        a = np.array(edit_sizes_stmts)
        low = np.percentile(a, 0)
        q1 = np.percentile(a, 25)
        median = np.percentile(a, 50)
        q3 = np.percentile(a, 75)
        high = np.percentile(a, 100)
        mean = np.mean(a)
        s = np.std(a)
        n = len(a)
        writer.writerow({'userId': prev_row['userId'], 'projectId': prev_row['projectId'], \
            'workSessionId': prev_ws, 'assignment': prev_row['cleaned_assignment'], \
            'min': low, 'q1': q1, 'q2': median, 'q3': q3, 'max': high, 'mean': mean, \
            's': s, 'n': n })

def get_launch_totals(infile, outfile):
    """
    Takes in work_sessions and prints out the total number of test
    launches and total number of regular launches for a project.

    Keyword arguments:
    infile  -- the file containing the work session data
    outfile -- the file to store the launch total data
    """
    print('Getting launch totals...')

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        fieldnames = ['userId', 'projectId', 'cleaned_assignment', 'normalLaunches', 'testLaunches']
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        prev_row = None
        normal_launches = 0
        test_launches = 0

        for row in reader:
            prev_row = prev_row or row

            if row['userId'] == prev_row['userId'] and row['projectId'] == prev_row['projectId'] \
                and row['cleaned_assignment'] == prev_row['cleaned_assignment']:
                    normal_launches += int(row['normalLaunches'])
                    test_launches += int(row['testLaunches'])
            else:
                writer.writerow({ 'userId': prev_row['userId'], 'projectId': prev_row['projectId'], \
                    'cleaned_assignment': prev_row['cleaned_assignment'], 'normalLaunches': normal_launches, \
                    'testLaunches': test_launches })

                normal_launches = 0
                test_launches = 0
            prev_row = row

def main(args):
    infile = args[1]
    outfile = args[2]
    try:
        if args[0] == 'summary':
            granularity = None
            if len(args) >= 4:
                granularity = args[3]
            subsession_summaries(infile, outfile, granularity)
        elif args[0] == 'launch_totals':
            get_launch_totals(infile, outfile)
        else:
            print_usage()

    except FileNotFoundError as e:
        print("Error! File %s does not exist." % infile)

def print_usage():
    print('Outputs launch stats from the provided input file. Stats are either ' +
        ' the quartiled number of statements added before each launch, or the ' +
        ' the total number of solution/test statements/methods changed before each ' +
        ' solution/test launch.')
    print('Usage:\n\t./stats.py launch_totals <input_file> <output_file>')
    print('OR\n\t./stats.py summary <input_file> <output_file> [WS]')
    print("IMPORTANT")
    print("* To get quartiles, use subsession data as input. To get totals, use worksession data.")
    print("* Make sure to use data that was generated from a 'cleaned' data file.")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print_usage()
        sys.exit()
    main(sys.argv[1:])
