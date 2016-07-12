#! /usr/python/env python3

import csv

def get_duplicated(infile, outfile):
    """
    Prints out data from import events that appear twice for the same
    userId, projectId, and timestamp, resulting a list of student projects
    that may have duplicated data.

    Keyword arguments:
    infile  -- the input file (CSV)
    outfile -- the output file (CSV)
    """
    print('Getting duplicated projects...')
    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        fieldnames = ['userId', 'projectId', 'timestamp', 'uri']
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict(fn, fn) for fn in writer.fieldnames)

        # Set initial values
        prev_row = None

        # Cache will have structure like this:
        # {
        #     userId: {
        #         projectId: {
        #             import event with timestamp
        #         }
        #     }
        # }
        cache = {}
