#! /usr/bin/env python3

import sys
import pandas as pd
import datetime

THRESHOLD = 5

def userworkunits(usergroup):
    current_unit_time = 0
    prev_row = None

    solution_edits_stmts = 0
    test_edits_stmts = 0
    solution_edits_bytes = 0
    test_edits_bytes = 0
    normal_launches = 0
    test_launches = 0

    curr_sizes_stmts = {}
    curr_sizes_bytes = {}

    for index, row in usergroup.iterrows():
        prev_row = prev_row or None

        prev_time = datetime.datetime.fromtimestamp(int(float(prev_row['time'])))
        time = datetime.datetime.fromtimestamp(int(float(row['time'])))
        diff = (time - prev_time).total_seconds() / 60 # minutes
        if (current_unit_time + diff <= THRESHOLD):
            current_unit_time += diff
        else:
            current_unit_time = 0

        testcase = int(row['onTestCase']) == 1
        eventtype = row['Type']
        classname = row['Class-Name']
        curr_bytes = int(row['Current-Size'])
        curr_stmts = int(row['Current-Statements'])

        if (eventtype == 'Edit' and classname != ''):
            prev_bytes = curr_sizes_bytes.get(classname, 0)
            edit_size_btyes = abs(curr_bytes - prev_bytes)
            curr_sizes_bytes[classname] = curr_bytes

            prev_stmts = curr_sizes_stmts.get(classname, 0)
            edit_size_btyes = abs(curr_bytes - prev_bytes)
            curr_sizes_bytes[classname] = curr_bytes


def workunits(infile, outfile=None):
    # Import data
    dtypes = {
        'userId': str,
        'projectId': str,
        'email': str,
        'CASSIGNMENTNAME': str,
        'time': int,
        'Class-Name': object,
        'Unit-Type': object,
        'Type': object,
        'Subtype': object,
        'Subsubtype': object,
        'onTestCase': object,
        'Current-Statements': object,
        'Current-Methods': object,
        'Current-Size': object
    }
    df = pd.read_csv(infile, dtype=dtypes, na_values=[], low_memory=False, usecols=list(dtypes.keys()))
    df.sort_values(by=['time'], ascending=[1], inplace=True)
    df.fillna('', inplace=True)
    print('1. Finished reading raw sensordata.')

    # Group data by unique values of userIds and assignment
    userdata = df.groupby(['userId', 'CASSIGNMENTNAME'])
    print('2. Finished grouping data. Calculating work units now.')

    results = userdata.apply(userworkunits)

    # Write out
    if outfile:
        results.to_csv(outfile)
    else:
        return results

def main(args):
    infile = args[0]
    outfile = args[1]

    try:
        earlyoften(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)

if __name__ == '__main__':
    print('This process is not yet implemented.')
