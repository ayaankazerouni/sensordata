#! /usr/bin/env python3

import sys
import csv
import datetime
import re
import json
import pandas as pd
import numpy as np

def userearlyoften(usergroup):
    """
    This function acts on data for one student's sensordata.

    Keyword arguments:
    usergroup -- pandas.DataFrame
    """
    prev_row = None
    total_weighted_edits_bytes = []
    total_edits_bytes = []
    total_weighted_edits_stmts = []
    total_edits_stmts = []
    total_weighted_solution_bytes = []
    total_solution_bytes = []
    total_weighted_solution_stmts = []
    total_solution_stmts = []
    total_weighted_test_bytes = []
    total_test_bytes = []
    total_weighted_test_stmts = []
    total_test_stmts = []
    total_weighted_solution_methods = []
    total_solution_methods = []
    total_weighted_test_methods = []
    total_test_methods = []
    total_weighted_launches = []
    total_weighted_test_launches = []
    total_weighted_normal_launches = []

    curr_sizes_bytes = {}
    curr_sizes_stmts = {}
    curr_sizes_methods = {}

    assignment_field = 'CASSIGNMENTNAME'
    if 'cleaned_assignment' in usergroup.columns:
        assignment_field = 'cleaned_assignment'

    first = usergroup.iloc[0]
    first_time = int(first['time'])
    term = get_term(first_time)
    first_assignment = first[assignment_field]
    number = int(re.search(r'\d', first_assignment).group())

    due_time = data[term]['assignment%d' % (number)]['dueTime']
    due_time = int(due_time)
    due_date = datetime.date.fromtimestamp(due_time / 1000)

    for index, row in usergroup.iterrows():
        prev_row = prev_row if prev_row is None else row

        time = int(float(row['time']))
        date = datetime.date.fromtimestamp(time / 1000)
        days_to_deadline = (due_date - date).days

        if days_to_deadline < -4:
            prev_row = row
            continue

        if (repr(row['Type']) == repr('Edit') and len(row['Class-Name']) > 0):
            class_name = repr(row['Class-Name'])
            curr_bytes = int(row['Current-Size'])
            curr_stmts = int(row['Current-Statements'])
            curr_methods = int(row['Current-Methods'])

            prev_bytes = curr_sizes_bytes.get(class_name, 0)
            prev_stmts = curr_sizes_stmts.get(class_name, 0)
            prev_methods = curr_sizes_methods.get(class_name, 0)

            byte_edit_size = abs(prev_bytes - curr_bytes)
            stmt_edit_size = abs(prev_stmts - curr_stmts)
            method_edit_size = abs(prev_methods - curr_methods)

            on_test_case = int(row['onTestCase']) == 1

            if byte_edit_size > 0:
                total_weighted_edits_bytes.append(byte_edit_size * days_to_deadline)
                total_edits_bytes.append(byte_edit_size)

                if on_test_case:
                    total_weighted_test_bytes.append(byte_edit_size * days_to_deadline)
                    total_test_bytes.append(byte_edit_size)
                else:
                    total_weighted_solution_bytes.append(byte_edit_size * days_to_deadline)
                    total_solution_bytes.append(byte_edit_size)

            if stmt_edit_size > 0:
                total_weighted_edits_stmts.append(stmt_edit_size * days_to_deadline)
                total_edits_stmts.append(stmt_edit_size)

                if on_test_case:
                    total_weighted_test_stmts.append(stmt_edit_size * days_to_deadline)
                    total_test_stmts.append(stmt_edit_size)
                else:
                    total_weighted_solution_stmts.append(stmt_edit_size * days_to_deadline)
                    total_solution_stmts.append(stmt_edit_size)

            if method_edit_size > 0:
                if on_test_case:
                    total_weighted_test_methods.append(method_edit_size * days_to_deadline)
                    total_test_methods.append(method_edit_size)
                else:
                    total_weighted_solution_methods.append(method_edit_size * days_to_deadline)
                    total_solution_methods.append(method_edit_size)

            curr_sizes_stmts[class_name] = curr_stmts
            curr_sizes_methods[class_name] = curr_methods
            curr_sizes_bytes[class_name] = curr_bytes
        elif (repr(row['Type']) == repr('Launch')):
            total_weighted_launches.append(days_to_deadline)

            if (repr(row['Subtype']) == repr('Test')):
                total_weighted_test_launches.append(days_to_deadline)
            elif (repr(row['Subtype']) == repr('Normal')):
                total_weighted_normal_launches.append(days_to_deadline)

        prev_row = row

    global finished
    finished = finished + 1
    percent = round((finished / ngroups) * 100)
    if percent in range(20, 30) or percent in range(50, 60)  or percent in range(70, 100):
        print("%d%% done" % percent)

    if (len(total_edits_stmts) > 0):
        byte_early_often_index = np.sum(total_weighted_edits_bytes) / np.sum(total_edits_bytes)
        stmt_early_often_index = np.sum(total_weighted_edits_stmts) / np.sum(total_edits_stmts)
        solution_byte_early_often_index = np.sum(total_weighted_solution_bytes) / np.sum(total_solution_bytes)
        solution_stmt_early_often_index = np.sum(total_weighted_solution_stmts) / np.sum(total_solution_stmts)
        solution_meth_early_often_index = np.sum(total_weighted_solution_methods) / np.sum(total_solution_methods)
        test_byte_early_often_index = np.sum(total_weighted_test_bytes) / np.sum(total_test_bytes)
        test_stmt_early_often_index = np.sum(total_weighted_test_stmts) / np.sum(total_test_stmts)
        test_meth_early_often_index = np.sum(total_weighted_test_methods) / np.sum(total_test_methods)
        launch_early_often = np.mean(total_weighted_launches)
        test_launch_early_often = np.mean(total_weighted_test_launches)
        normal_launch_early_often = np.mean(total_weighted_normal_launches)

        to_write = {
            'projectId': prev_row['projectId'],
            'CASSIGNMENTNAME': prev_row['CASSIGNMENTNAME'],
            'email': prev_row['email'],
            'stmtEarlyOftenIndex': stmt_early_often_index,
            'byteEarlyOftenIndex': byte_early_often_index,
            'solutionByteEarlyOftenIndex': solution_byte_early_often_index,
            'solutionStmtEarlyOftenIndex': solution_stmt_early_often_index,
            'solutionMethodsEarlyOftenIndex': solution_meth_early_often_index,
            'testByteEarlyOftenIndex': test_byte_early_often_index,
            'testStmtsEarlyOftenIndex': test_stmt_early_often_index,
            'testMethodsEarlyOftenIndex': test_meth_early_often_index,
            'launchEarlyOften': launch_early_often,
            'testLaunchEarlyOften': test_launch_early_often,
            'normalLaunchEarlyOften': normal_launch_early_often
        }

        return pd.Series(to_write)
    else:
        return None

def earlyoften(infile, outfile=None):
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
    print('1. Finished reading CSV.')

    # Group data by unique values of userIds and assignment
    userdata = df.groupby(['userId'])
    print('2. Finished grouping data. Applying function now.')

    global data
    with open('due_times.json') as data_file:
        data = json.load(data_file)

    global finished
    finished = 0
    global ngroups
    ngroups = len(userdata)
    results = userdata.apply(userearlyoften)

    # Write out
    if outfile:
        results.to_csv(outfile)
    else:
        return results

def get_term(timestamp):
    """
    Expects a timestamp in milliseconds.
    """
    fall_time = 1452877947000
    spring_time = 1471281147000
    if timestamp >= fall_time:
        return 'fall2016'

    if timestamp >= spring_time:
        return 'spring2016'
    else:
        return None

def main(args):
    infile = args[0]
    outfile = args[1]
    deadline = int(args[2]) if len(args) > 2 else None
    try:
        earlyoften(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Calculates an early/often index for each student project for a given assignment.')
        print('Early/often is the [sum of (editSize * daysToDeadline) / totalEditSize].')
        print('Usage:\n\t./early_often.py <input file> <output file> <assignment deadline as a millisecond timestamp>')
        sys.exit()
    main(sys.argv[1:])
