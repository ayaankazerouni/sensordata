#! /usr/bin/env python3

import argparse
import pandas as pd
from datetime import datetime

def userworksessions(usergroup, threshold=3):
    prev_row = None
    ws = None
    test_launches = 0
    normal_launches = 0
    start_time = None
    edit_size_stmts = 0
    test_edit_size_stmts = 0
    curr_sizes_stmts = {}
    normal_launches = 0
    test_launches = 0
    ws_start_time = None
    ws = 0

    userresult = None

    for index, row in usergroup.iterrows():
        prev_row = row if prev_row is None else prev_row

        prev_time = int(float(prev_row['time']))
        prev_timestamp = datetime.fromtimestamp(prev_time / 1000)
        curr_time = int(float(row['time']))
        curr_timestamp = datetime.fromtimestamp(curr_time / 1000)
        hours = (curr_timestamp - prev_timestamp).total_seconds() / 3600
        ws_start_time = ws_start_time or curr_time

        new_ws = hours >= threshold

        if new_ws:
            to_write = {
                'userId': row['userId'],
                'email': row['email'],
                'projectId': row['projectId'],
                'CASSIGNMENTNAME': row['CASSIGNMENTNAME'],
                'workSessionId': ws,
                'start_time': ws_start_time,
                'end_time': prev_time,
                'normalLaunches': normal_launches,
                'testLaunches': test_launches,
                'editSizeStmts': edit_size_stmts,
                'testEditSizeStmts': test_edit_size_stmts
            }
            resultrow = pd.Series(to_write)
            if userresult is None:
                userresult = pd.DataFrame([resultrow])
            else:
                userresult = userresult.append(other=resultrow, ignore_index=True)

            # result persistent counts for next work session
            ws_start_time = curr_time
            prev_time = curr_time
            edit_size_stmts = 0
            test_edit_size_stmts = 0
            normal_launches = 0
            test_launches = 0
            ws += 1

        if (repr(row['Type']) == repr('Edit') and len(row['Class-Name']) > 0):
            class_name = repr(row['Class-Name'])
            curr_stmts = int(row['Current-Statements'])
            prev_stmts = curr_sizes_stmts.get(class_name, 0)
            edit_size = abs(prev_stmts - curr_stmts)
            curr_sizes_stmts[class_name] = curr_stmts

            on_test_case = int(row['onTestCase']) == 1
            if on_test_case:
                test_edit_size_stmts += edit_size
            else:
                edit_size_stmts += edit_size
        elif (repr(row['Type']) == repr('Launch')):
            test_launch = repr(row['Subtype']) == 'Test'
            if test_launch:
                test_launches += 1
            else:
                normal_launches += 1

        prev_row = row
    return userresult


def worksessions(infile, outfile=None):
    print('Getting worksessions...')
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
    print('\tReading raw sensordata')
    df = pd.read_csv(infile, dtype=dtypes, na_values=[], low_memory=False, usecols=list(dtypes.keys()))
    df.sort_values(by=['time'], ascending=[1], inplace=True)
    df.fillna('', inplace=True)

    print('\tGrouping student projects')
    userdata = df.groupby(['userId'])
    print('\tCalculating worksessions. This could take some time...')
    results = userdata.apply(userworksessions, threshold=3)

    if outfile is None:
        return results
    else:
        results.to_csv(outfile)
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile',
        help='path to raw sensordata for multiple students working on a single assignment')
    parser.add_argument('--outfile', '-o',
        help='path to desired output file for work_session data',
        default=None)
    args = parser.parse_args()

    infile = args.infile
    outfile = args.outfile
    results = worksessions(infile, outfile) # may be None
