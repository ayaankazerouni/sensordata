#!/usr/bin/env python3

"""Calculates incremental development metrics in the form
of Early/Often indices. 

Simply put, an early often index
is the mean amount of code written on a given day leading
up to the project due date. We calculate similar metrics
for [solution/test] code writing and [solution/test] launches.

To use:
    from early_often import earlyoften, or
    ./early_often.py <input file> <web-cat submissions file> <duedates file> <output file> on the command line
"""

from utils import get_term
from load_datasets import load_submission_data

import sys
import datetime
import re
import json
import pandas as pd
import numpy as np

def userearlyoften(usergroup, due_date_data, submissions, usercol='userId', lognosubs=False):
    """
    This function acts on data for one student's sensordata.
    Generally, it is invoked by earlyoften in a split-apply-combine procedure.

    Args:
        usergroup (DataFrame): Event stream for a student working on a single project
        due_date_data (dict): Dictionary containing due dates in millisecond timestamps 
        submissions (DataFrame): Last submission from each student
        usercol (str): Name of the column identifying the user (default "userId")
        lognosubs (bool): Print a message for users for whom submissions were not found?

    Returns:
        A *DataFrame* containing the early often measurements for the user on a given assignment.
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
    total_weighted_debug_sessions = []

    curr_sizes_bytes = {}
    curr_sizes_stmts = {}
    curr_sizes_methods = {}
    curr_test_assertions = {} # for each file

    user_id, assignment = usergroup.name # returns a tuple

    # get the term and assignment due date
    first = usergroup.iloc[0]
    first_time = first['time']
    epoch = datetime.datetime.utcfromtimestamp(0) # seconds
    first_time = (first_time - epoch).total_seconds()
        
    term = get_term(first_time)
    assignment_number = int(re.search(r'\d', assignment).group())

    due_time = due_date_data[term]['assignment%d' % (assignment_number)]['dueTime']
    due_time = int(due_time)
    due_date = datetime.date.fromtimestamp(due_time / 1000)

    if usercol == 'email':
        user_id = user_id.split('@')[0]
    
    try:
        lastsubmissiontime = submissions.loc[user_id, 'Project {}'.format(assignment_number)]['submissionTimeRaw']
    except KeyError:
        # Either the user or the assignment is not present in the submission list.
        # Extract the information manually.
        if lognosubs:
            print('Cannot find final submission for {} on Project {}'.format(user_id, assignment_number))
        return None

    for index, row in usergroup.iterrows():
        prev_row = row if prev_row is None else prev_row
    
        time = row['time']
        date = time.date()
        days_to_deadline = (due_date - date).days

        if time > lastsubmissiontime or days_to_deadline < -4:
            prev_row = row
            continue

        if repr(row['Type']) == repr('Edit') and len(row['Class-Name']) > 0:
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
        elif (repr(row['Type']) == repr('DebugSession')):
            length = float(row['length'])
            if length > 30:
                total_weighted_debug_sessions.append(days_to_deadline)

        prev_row = row

    byte_early_often_index = np.sum(total_weighted_edits_bytes) / np.sum(total_edits_bytes)
    stmt_early_often_index = np.sum(total_weighted_edits_stmts) / np.sum(total_edits_stmts)
    solution_byte_early_often_index = np.sum(total_weighted_solution_bytes) / np.sum(total_solution_bytes)
    solution_stmt_early_often_index = np.sum(total_weighted_solution_stmts) / np.sum(total_solution_stmts)
    solution_meth_early_often_index = np.sum(total_weighted_solution_methods) / np.sum(total_solution_methods)
    test_byte_early_often_index = np.sum(total_weighted_test_bytes) / np.sum(total_test_bytes)
    test_stmt_early_often_index = np.sum(total_weighted_test_stmts) / np.sum(total_test_stmts)
    test_meth_early_often_index = np.sum(total_weighted_test_methods) / np.sum(total_test_methods)
    test_assrt_early_often_index = np.sum(total_weighted_test_assertions) / np.sum(total_test_assertions)
    launch_early_often = np.mean(total_weighted_launches)
    launch_median = np.median(total_weighted_launches)
    launch_sd = np.std(total_weighted_launches)
    test_launch_early_often = np.mean(total_weighted_test_launches)
    test_launch_median = np.median(total_weighted_test_launches)
    test_launch_sd = np.std(total_weighted_test_launches)
    normal_launch_early_often = np.mean(total_weighted_normal_launches)
    normal_launch_median = np.median(total_weighted_normal_launches)
    normal_launch_sd = np.std(total_weighted_normal_launches)
    debug_session_early_often = np.mean(total_weighted_debug_sessions)
    debug_session_median = np.median(total_weighted_debug_sessions)
    debug_session_sd = np.std(total_weighted_debug_sessions)

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
        'assertionsEarlyOftenIndex': test_assrt_early_often_index,
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
        'normalLaunchSd': normal_launch_sd,
        'debugSessionEarlyOften': debug_session_early_often,
        'debugSessionMedian': debug_session_median,
        'debugSessionSd': debug_session_sd
    }

    return pd.Series(to_write)

def earlyoften(infile, submissionpath, duetimepath, outfile=None, dtypes=None, date_parser=None):
    """Calculate Early/Often indices for developers based on IDE events.
    Early/Often refers to the mean time of a certain type of event, in terms of
    "days until the deadline". Applying the same concept, we also calculate
    medians and standard deviations.
    
    Args:
        infile (str): Path to a file containing raw SensorData
        outfile (str, optional): Path to a file where combined early often metrics should be written (optional). 
            If *None*, output is written to a Pandas DataFrame.
        submissionpath (str): Path to Web-CAT submissions. Used only to determine the time of the final submission.
        duetimepath (str): Path to a JSON file containing due date data for assignments in different terms.
        dtypes (dict, optional, no-CLI): Column data types (also only reads the specified columns)
        date_parser (func, optional, no-CLI): A function or lambda to parse timestamps.

    Returns:
        A *DataFrame* if no *outfile* is specified. *None* otherwise.
    """
    submissions = load_submission_data(submissionpath)
    print('0. Finished reading submission data.')

    # Import event stream for all students 
    if not dtypes:
        dtypes = {
            'userId': str,
            'projectId': str,
            'email': str,
            'CASSIGNMENTNAME': str,
            'time': str,
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

    if not date_parser:
        # assume timestamps are in milliseconds since the epoch unless specified
        date_parser = lambda d: datetime.datetime.fromtimestamp(int(d) / 1000)
    df = pd.read_csv(infile, dtype=dtypes, na_values=[], low_memory=False, usecols=list(dtypes.keys()), 
            date_parser=date_parser, parse_dates=['time']) \
            .sort_values(by=['time'], ascending=[1]) \
            .fillna('')
    print('1. Finished reading raw sensordata.')
    
    # Group data by student and project 
    if 'userId' in df.columns:
        user_id = 'userId'
    elif 'email' in df.columns:
        user_id = 'email' 
    else:
        user_id = 'userName'

    assignmentcol = 'assignment'
    if 'cleaned_assignment' in df.columns:
        assignmentcol = 'cleaned_assignment'
    elif 'CASSIGNMENTNAME' in df.columns:
        assignmentcol = 'CASSIGNMENTNAME'

    grouped = df.groupby([user_id, assignmentcol])
    print('2. Finished grouping data. Calculating measures now. This could take some time...')
    
    due_date_data = None
    with open(duetimepath) as data_file:
        due_date_data = json.load(data_file)

    results = grouped.apply(userearlyoften, 
                due_date_data=due_date_data, 
                submissions=submissions, 
                usercol=user_id)

    # Write out
    if outfile:
        results.to_csv(outfile)
    else:
        return results


def main(args):
    """Parses CLI arguments and begins execution."""
    infile = args[0]
    submissionpath = args[1]
    duetimepath = args[2]
    outfile = args[3]
    if args.length > 4:
        dateformat = args[4]
    else:
        dateformat = None

    try:
       results = earlyoften(infile=infile, submissionpath=submissionpath, duetimepath=duetimepath, outfile=outfile, dateformat=dateformat) # If outfile is None, stores results in memory
    except FileNotFoundError:
        print("Error! File '%s' does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit()
    main(sys.argv[1:])
