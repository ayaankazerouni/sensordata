#! /usr/bin/env python3

import sys
import csv
import datetime
import pandas as pd
import numpy as np

def userearlyoften(usergroup):
    """
    This function acts on data for one student's sensordata.

    Keyword arguments:
    usergroup -- pandas.DataFrame
    """
    prev_row = None
    total_weighted_edit_size = 0
    total_edit_size = 0
    total_weighted_solution_edits = 0
    total_solution_edits = 0
    total_weighted_test_edits = 0
    total_test_edits = 0
    total_weighted_solution_methods = 0
    total_solution_methods = 0
    total_weighted_test_methods = 0
    total_test_methods = 0
    total_launches = 0
    total_weighted_launches = 0
    total_test_launches = 0
    total_weighted_test_launches = 0
    total_normal_launches = 0
    total_weighted_normal_launches = 0

    curr_sizes = {}
    curr_sizes_methods = {}

    assignment_field = 'CASSIGNMENTNAME'
    if 'cleaned_assignment' in usergroup.columns:
        assignment_field = 'cleaned_assignment'

    for index, row in usergroup.iterrows():
        prev_row = row if prev_row is None else prev_row

        time = int(float(row['time']))
        date = datetime.date.fromtimestamp(time / 1000)
        days_to_deadline = (due_date - date).days

        if days_to_deadline < -4:
            prev_row = row
            continue

        if (repr(row['Type']) == repr('Edit') and len(row['Class-Name']) > 0):
            class_name = repr(row['Class-Name'])
            curr_size = int(row['Current-Statements'])
            curr_methods = int(row['Current-Methods'])

            prev_size = curr_sizes.get(class_name, 0)
            prev_methods = curr_sizes_methods.get(class_name, 0)

            edit_size = abs(prev_size - curr_size)
            method_edit_size = abs(prev_methods - curr_methods)

            total_weighted_edit_size += (edit_size * days_to_deadline)
            total_edit_size += edit_size

            if (int(row['onTestCase']) == 1):
                total_weighted_test_edits += (edit_size * days_to_deadline)
                total_test_edits += edit_size
                total_weighted_test_methods += (method_edit_size * days_to_deadline)
                total_test_methods += method_edit_size
            else:
                total_weighted_solution_edits += (edit_size * days_to_deadline)
                total_solution_edits += edit_size
                total_weighted_solution_methods += (method_edit_size *  days_to_deadline)
                total_solution_methods += method_edit_size

            curr_sizes[class_name] = curr_size
            curr_sizes_methods[class_name] = curr_methods
        elif (repr(row['Type']) == repr('Launch')):
            total_launches += 1
            total_weighted_launches += days_to_deadline

            if (repr(row['Subtype']) == repr('Test')):
                total_test_launches += 1
                total_weighted_test_launches += days_to_deadline
            elif (repr(row['Subtype']) == repr('Normal')):
                total_normal_launches += 1
                total_weighted_normal_launches += days_to_deadline

        prev_row = row

    if (total_edit_size > 0):
        early_often_index = total_weighted_edit_size / total_edit_size
        solution_stmt_early_often_index = total_weighted_solution_edits / total_solution_edits if total_solution_edits > 0 else None
        solution_meth_early_often_index = total_weighted_solution_methods / total_solution_methods if total_solution_methods > 0 else None
        test_stmt_early_often_index = total_weighted_test_edits / total_test_edits if total_test_edits > 0 else None
        test_meth_early_often_index = total_weighted_test_methods / total_test_methods if total_test_methods > 0 else None
        launch_early_often = total_weighted_launches / total_launches if total_launches > 0 else None
        test_launch_early_often = total_weighted_test_launches / total_test_launches if total_test_launches > 0 else None
        normal_launch_early_often = total_weighted_normal_launches / total_normal_launches if total_normal_launches > 0 else None

        to_write = {
            'projectId': prev_row['projectId'],
            'userId': prev_row['userId'],
            'email': prev_row['email'],
            'CASSIGNMENTNAME': prev_row[assignment_field],
            'earlyOftenIndex': early_often_index,
            'solutionStmtEarlyOftenIndex': solution_stmt_early_often_index,
            'solutionMethodsEarlyOftenIndex': solution_meth_early_often_index,
            'testStmtsEarlyOftenIndex': test_stmt_early_often_index,
            'testMethodsEarlyOftenIndex': test_meth_early_often_index,
            'launchEarlyOften': launch_early_often,
            'testLaunchEarlyOften': test_launch_early_often,
            'normalLaunchEarlyOften': normal_launch_early_often
        }

        return pd.Series(to_write)
    else:
        return None

def earlyoften(infile, outfile, deadline):
    # Import data
    dtypes={
        'time': int,
        'Class-Name': object,
        'Unit-Type': object,
        'Type': object,
        'Subtype': object,
        'Subsubtype': object,
        'onTestCase': object,
        'Current-Statements': object,
        'Current-Methods': object
    }
    df = pd.read_csv(infile, dtype=dtypes, na_values=[])
    df.sort_values(by=['userId', 'time'], ascending=[1,1], inplace=True)
    df.fillna('', inplace=True)

    # Group data by unqiue values of userIds
    userdata = df.groupby(['userId'])

    global due_date
    due_date = datetime.date.fromtimestamp(deadline / 1000)
    results = userdata.apply(userearlyoften)

    # Write out
    results.to_csv(outfile)

def main(args):
    infile = args[0]
    outfile = args[1]
    deadline = int(args[2])
    try:
        earlyoften(infile, outfile, deadline)
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Calculates an early/often index for each student project for a given assignment.')
        print('Early/often is the [sum of (editSize * daysToDeadline) / totalEditSize].')
        print('Usage:\n\t./early_often.py <input file> <output file> <assignment deadline as a millisecond timestamp>')
        sys.exit()
    main(sys.argv[1:])
