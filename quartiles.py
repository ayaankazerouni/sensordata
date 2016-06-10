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

    edit_sizes = []
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
                    edit_sizes.append(int(row['editSize']))

                    prev_row = row
            else:
                prev_ws = int(prev_row['workSessionId'])
                a = np.array(edit_sizes)
                low = np.percentile(a, 0)
                q1 = np.percentile(a, 25)
                median = np.percentile(a, 50)
                q3 = np.percentile(a, 75)
                high = np.percentile(a, 100)
                writer.writerow({'workSessionId': prev_ws, 'q1': q1, 'q2': median, 'q3': q3})

                edit_sizes = []
                edit_sizes.append(int(row['editSize']))
                prev_row = row

        prev_ws = int(prev_row['workSessionId'])
        a = np.array(edit_sizes)
        low = np.percentile(a, 0)
        q1 = np.percentile(a, 25)
        median = np.percentile(a, 50)
        q3 = np.percentile(a, 75)
        high = np.percentile(a, 100)
        writer.writerow({'workSessionId': prev_ws, 'q1': q1, 'q2': median, 'q3': q3})

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        get_launch_quartiles(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File %s does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Splits a subsession data file into quartiles based on statements changed ' +
            'per subsession.')
        print('Usage: ./quartiles.py [input_file] [output_file]')
        sys.exit()
    main(sys.argv[1:])
