#! /usr/bin/env python3

import csv
import numpy as np
import sys

def get_launch_quartiles(infile, outfile):
    """
    Splits a subsession data file into quartiles based on edits
    per subsession for easier visualisations.

    Keyword arguments:
    infile  -- the name of the file containing subsession data
    outfile -- the name of the file in which to put quartile data
    """
    print('Getting edits-per-launch quartiles...')
    fieldnames = ['workSessionId', 'q1', 'q2', 'q3']

    edit_sizes_stmts = []
    prev_row = None


    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        for row in reader:
            prev_row = prev_row or row
            if (row['workSessionId'] == prev_row['workSessionId'] \
                and row['projectId'] == prev_row['projectId']):
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
                writer.writerow({'workSessionId': prev_ws, 'q1': q1, 'q2': median, 'q3': q3})

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
        writer.writerow({ 'workSessionId': prev_ws, 'q1': q1, 'q2': median, 'q3': q3 })

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
        fieldnames = ['userId', 'projectId', 'assignment', 'normalLaunches', 'testLaunches']
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
                and row['assignment'] == prev_row['assignment']:
                    normal_launches += int(row['normalLaunches'])
                    test_launches += int(row['testLaunches'])
            else:
                writer.writerow({ 'userId': prev_row['userId'], 'projectId': prev_row['projectId'], \
                    'assignment': prev_row['assignment'], 'normalLaunches': normal_launches, \
                    'testLaunches': test_launches })

                normal_launches = 0
                test_launches = 0
            prev_row = row

def main(args):
    infile = args[1]
    outfile = args[2]
    try:
        if args[0] == 'quartiles':
            get_launch_quartiles(infile, outfile)
        elif args[0] == 'totals':
            get_launch_totals(infile, outfile)
        else:
            print_usage()

    except FileNotFoundError as e:
        print("Error! File %s does not exist." % infile)

def print_usage():
    print('Splits a subsession data file into quartiles based on statements changed ' +
        'per subsession.')
    print('Usage: ./launch_stats.py (quartiles|totals) [input_file] [output_file]')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print_usage()
        sys.exit()
    main(sys.argv[1:])
