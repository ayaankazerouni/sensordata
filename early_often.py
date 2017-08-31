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
    total_test_assertions = []
    total_weighted_test_assertions = []

    curr_sizes_bytes = {}
    curr_sizes_stmts = {}
    curr_sizes_methods = {}
    curr_test_assertions = {} # for each file

    assignment_field = 'CASSIGNMENTNAME'
    if 'cleaned_assignment' in usergroup.columns:
        assignment_field = 'cleaned_assignment'

    first = usergroup.iloc[0]
    first_time = int(first['time'])
    term = get_term(first_time)
    first_assignment = first[assignment_field]
    assignment_number = int(re.search(r'\d', first_assignment).group())
    user_id = first['email'].split('@')[0]

    due_time = data[term]['assignment%d' % (assignment_number)]['dueTime']
    due_time = int(due_time)
    due_date = datetime.date.fromtimestamp(due_time / 1000)

    lastsubmissiontime = submissions.loc[user_id,'Project %d' % assignment_number]['submissionTimeRaw']

    for index, row in usergroup.iterrows():
        prev_row = prev_row if prev_row is None else row

        time = int(float(row['time']))
        date = datetime.date.fromtimestamp(time / 1000)
        days_to_deadline = (due_date - date).days

        if time > lastsubmissiontime or days_to_deadline < -4:
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

            assertion_change_size = 0
            if row['Current-Test-Assertions'] != '':
                curr_assertions = int(row['Current-Test-Assertions']) # for the current file
                prev_assertions = curr_test_assertions.get(class_name, 0)
                assertion_change_size = abs(prev_assertions - curr_assertions)
                curr_test_assertions[class_name] = curr_assertions

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

            if assertion_change_size > 0:
                total_weighted_test_assertions.append(assertion_change_size * days_to_deadline)
                total_test_assertions.append(assertion_change_size)

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

    if (len(total_edits_bytes) > 0):
        byte_early_often_index = np.sum(total_weighted_edits_bytes) / np.sum(total_edits_bytes)
        stmt_early_often_index = np.sum(total_weighted_edits_stmts) / np.sum(total_edits_stmts)
        solution_byte_early_often_index = np.sum(total_weighted_solution_bytes) / np.sum(total_solution_bytes)
        solution_stmt_early_often_index = np.sum(total_weighted_solution_stmts) / np.sum(total_solution_stmts)
        solution_meth_early_often_index = np.sum(total_weighted_solution_methods) / np.sum(total_solution_methods)
        test_byte_early_often_index = np.sum(total_weighted_test_bytes) / np.sum(total_test_bytes)
        test_stmt_early_often_index = np.sum(total_weighted_test_stmts) / np.sum(total_test_stmts)
        test_meth_early_often_index = np.sum(total_weighted_test_methods) / np.sum(total_test_methods)
        test_assertion_early_often_index = np.sum(total_weighted_test_assertions) / np.sum(total_test_assertions)
        launch_early_often = np.mean(total_weighted_launches)
        launch_median = np.median(total_weighted_launches)
        launch_sd = np.std(total_weighted_launches)
        test_launch_early_often = np.mean(total_weighted_test_launches)
        test_launch_median = np.median(total_weighted_test_launches)
        test_launch_sd = np.std(total_weighted_test_launches)
        normal_launch_early_often = np.mean(total_weighted_normal_launches)
        normal_launch_median = np.median(total_weighted_normal_launches)
        normal_launch_sd = np.std(total_weighted_normal_launches)

        stretched_bytes = []
        for weighted, unweighted in zip(total_weighted_edits_bytes, total_edits_bytes):
            relative_time = weighted / unweighted
            for i in range(weighted):
                stretched_bytes.append(relative_time)

        byte_edit_median = np.median(stretched_bytes)
        byte_edit_sd = np.std(stretched_bytes)

        stretched_solution_bytes = []
        for weighted, unweighted in zip(total_weighted_solution_bytes, total_solution_bytes):
            relative_time = weighted / unweighted
            for i in range(weighted):
                stretched_solution_bytes.append(relative_time)

        solution_byte_edit_median = np.median(stretched_solution_bytes)
        solution_byte_edit_sd = np.std(stretched_solution_bytes)

        stretched_test_bytes = []
        for weighted, unweighted in zip(total_weighted_test_bytes, total_test_bytes):
            relative_time = weighted / unweighted
            for i in range(weighted):
                stretched_test_bytes.append(relative_time)

        test_byte_edit_median = np.median(stretched_test_bytes)
        test_byte_edit_sd = np.std(stretched_test_bytes)

        stretched_stmts = []
        for weighted, unweighted in zip(total_weighted_edits_stmts, total_edits_stmts):
            relative_time = weighted / unweighted
            for i in range(weighted):
                stretched_stmts.append(relative_time)

        stmt_edit_median = np.median(stretched_stmts)
        stmt_edit_sd = np.std(stretched_stmts)

        stretched_assertions = []
        for weighted, unweighted in zip(total_weighted_test_assertions, total_test_assertions):
            relative_time = weighted / unweighted
            for i in range(weighted):
                stretched_assertions.append(relative_time)

        test_assertion_median = np.median(stretched_assertions)
        test_assertion_sd = np.std(stretched_assertions)

        to_write = {
            'projectId': prev_row['projectId'],
            'assignment': prev_row['CASSIGNMENTNAME'],
            'email': prev_row['email'],
            'byteEarlyOftenIndex': byte_early_often_index,
            'byteEditMedian': byte_edit_median,
            'byteEditSd': byte_edit_sd,
            'stmtEarlyOftenIndex': stmt_early_often_index,
            'stmtEditMedian': stmt_edit_median,
            'stmtEditSd': stmt_edit_sd,
            'solutionByteEarlyOftenIndex': solution_byte_early_often_index,
            'solutionByteEditMedian': solution_byte_edit_median,
            'solutionByteEditSd': solution_byte_edit_sd,
            'solutionStmtEarlyOftenIndex': solution_stmt_early_often_index,
            'solutionMethodsEarlyOftenIndex': solution_meth_early_often_index,
            'testByteEarlyOftenIndex': test_byte_early_often_index,
            'testByteEditMedian': test_byte_edit_median,
            'testByteEditSd': test_byte_edit_sd,
            'testStmtsEarlyOftenIndex': test_stmt_early_often_index,
            'testMethodsEarlyOftenIndex': test_meth_early_often_index,
            'assertionsEarlyOftenIndex': test_assertion_early_often_index,
            'assertionsMedian': test_assertion_median,
            'assertionSd': test_assertion_sd,
            'launchEarlyOften': launch_early_often,
            'launchMedian': launch_median,
            'launchSd': launch_sd,
            'testLaunchEarlyOften': test_launch_early_often,
            'testLaunchMedian': test_launch_median,
            'testLaunchSd': test_launch_sd,
            'normalLaunchEarlyOften': normal_launch_early_often,
            'normalLaunchMedian': normal_launch_median,
            'normalLaunchSd': normal_launch_sd
        }

        return pd.Series(to_write)
    else:
        return None

def earlyoften(infile, outfile=None):
    # Import due date data
    dtypes = {
        'userName': str,
        'assignment': str,
        'submissionNo': int,
        'submissionTimeRaw': float
    }
    global submissions
    submissions = pd.read_csv('data/fall-2016/web-cat-students-with-sensordata.csv',
        dtype=dtypes, usecols=list(dtypes.keys()))
    submissions.sort_values(by=['userName', 'assignment', 'submissionNo'], ascending=[1,1,0], inplace=True)
    submissions = submissions.groupby(['userName', 'assignment']).first()
    print('0. Finished reading submission data.')

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
        'Current-Size': object,
        'Current-Test-Assertions': object
    }
    df = pd.read_csv(infile, dtype=dtypes, na_values=[], low_memory=False, usecols=list(dtypes.keys()))
    df.sort_values(by=['time'], ascending=[1], inplace=True)
    df.fillna('', inplace=True)
    print('1. Finished reading raw sensordata.')

    # Group data by unique values of userIds and assignment
    userdata = df.groupby(['userId'])
    print('2. Finished grouping data. Calculating measures now.')

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

    try:
        earlyoften(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Calculates edit statistics for students from raw sensordata.')
        print('Usage:\n\t./early_often.py <input file> <output file>')
        sys.exit()
    main(sys.argv[1:])
