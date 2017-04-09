#! /usr/bin/env python3

import sys
import csv
import datetime
import numpy as np

def early_often_scores(infile, outfile, deadline):
    """
    Computes early-often metrics for each student project, based
    on the project deadline.

    * Early-often index on test|solution|all statements|methods

    for a total of 6 metrics.

    This script must be run on data from one particular assignment,
    since you pass it only one deadline.

    Keyword arguments:
    infile   -- the CSV input file containing raw sensordata
    outfile  -- the CSV output file
    deadline -- the project deadline in the form of a UNIX timestamp in milliseconds
    """
    print('Getting early/often scores...')

    fieldnames = [
        'projectId',
        'userId',
        'email',
        'CASSIGNMENTNAME',
        'earlyOftenIndex',
        'lineEditMean',
        'lineEditMedian',
        'lineEditSd',
        'skewness',
        'solutionStmtEarlyOftenIndex',
        'solutionMethodsEarlyOftenIndex',
        'testStmtsEarlyOftenIndex',
        'testMethodsEarlyOftenIndex',
        'launchEarlyOften',
        'testLaunchEarlyOften',
        'normalLaunchEarlyOften'
    ]

    due_date = datetime.date.fromtimestamp(deadline / 1000)

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        headers = next(reader)
        assignment_field = 'CASSIGNMENTNAME'
        if 'cleaned_assignment' in headers.keys():
            assignment_field = 'cleaned_assignment'
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        prev_row = None
        total_weighted_edit_size = []
        total_edit_size = []
        total_weighted_solution_edits = []
        total_solution_edits = []
        total_weighted_test_edits = []
        total_test_edits = []
        total_weighted_solution_methods = []
        total_solution_methods = []
        total_weighted_test_methods = []
        total_test_methods = []
        total_weighted_launches = []
        total_weighted_test_launches = []
        total_weighted_normal_launches = []

        curr_sizes = {}
        curr_sizes_methods = {}

        for row in reader:
            prev_row = prev_row or row

            time = int(float(row['time']))
            date = datetime.date.fromtimestamp(time / 1000)
            days_to_deadline = (due_date - date).days

            if days_to_deadline < -4:
                prev_row = row
                continue

            if (row['userId'] == prev_row['userId']):
                if (repr(row['Type']) == repr('Edit') and len(row['Class-Name']) > 0):
                    class_name = repr(row['Class-Name'])
                    curr_size = int(row['Current-Statements'])
                    curr_methods = int(row['Current-Methods'])

                    prev_size = curr_sizes.get(class_name, 0)
                    prev_methods = curr_sizes_methods.get(class_name, 0)

                    edit_size = abs(prev_size - curr_size)
                    method_edit_size = abs(prev_methods - curr_methods)

                    total_weighted_edit_size.append((edit_size * days_to_deadline))
                    total_edit_size.append(edit_size)

                    if (int(row['onTestCase']) == 1):
                        total_weighted_test_edits.append((edit_size * days_to_deadline))
                        total_test_edits.append(edit_size)
                        total_weighted_test_methods.append(method_edit_size * days_to_deadline)
                        total_test_methods.append(method_edit_size)
                    else:
                        total_weighted_solution_edits.append(edit_size * days_to_deadline)
                        total_solution_edits.append(edit_size)
                        total_weighted_solution_methods.append(method_edit_size *  days_to_deadline)
                        total_solution_methods.append(method_edit_size)

                    curr_sizes[class_name] = curr_size
                    curr_sizes_methods[class_name] = curr_methods
                elif (repr(row['Type']) == repr('Launch')):
                    total_weighted_launches.append(days_to_deadline)

                    if (repr(row['Subtype']) == repr('Test')):
                        total_weighted_test_launches.append(days_to_deadline)
                    elif (repr(row['Subtype']) == repr('Normal')):
                        total_weighted_normal_launches.append(days_to_deadline)

                prev_row = row
            else:
                if (len(total_edit_size) > 0):
                    early_often_index = np.sum(total_weighted_edit_size) / np.sum(total_edit_size)
                    line_edit_mean = np.mean(total_weighted_edit_size)
                    line_edit_sd = np.std(total_weighted_edit_size)
                    line_edit_med = np.median(total_weighted_edit_size)
                    skewness = (line_edit_mean - line_edit_med) * 3 / line_edit_sd
                    solution_stmt_early_often_index = np.sum(total_weighted_solution_edits) / np.sum(total_solution_edits)
                    solution_meth_early_often_index = np.sum(total_weighted_solution_methods) / np.sum(total_solution_methods)
                    test_stmt_early_often_index = np.sum(total_weighted_test_edits) / np.sum(total_test_edits)
                    test_meth_early_often_index = np.sum(total_weighted_test_methods) / np.sum(total_test_methods)
                    launch_early_often = np.mean(total_weighted_launches)
                    test_launch_early_often = np.mean(total_weighted_test_launches)
                    normal_launch_early_often = np.mean(total_weighted_normal_launches)

                    to_write = {
                        'projectId': prev_row['projectId'],
                        'userId': prev_row['userId'],
                        'email': prev_row['email'],
                        'CASSIGNMENTNAME': prev_row[assignment_field],
                        'earlyOftenIndex': early_often_index,
                        'lineEditMean': line_edit_mean,
                        'lineEditMedian': line_edit_med,
                        'lineEditSd': line_edit_sd,
                        'skewness': skewness,
                        'solutionStmtEarlyOftenIndex': solution_stmt_early_often_index,
                        'solutionMethodsEarlyOftenIndex': solution_meth_early_often_index,
                        'testStmtsEarlyOftenIndex': test_stmt_early_often_index,
                        'testMethodsEarlyOftenIndex': test_meth_early_often_index,
                        'launchEarlyOften': launch_early_often,
                        'testLaunchEarlyOften': test_launch_early_often,
                        'normalLaunchEarlyOften': normal_launch_early_often
                    }
                    writer.writerow(to_write)

                total_weighted_edit_size = []
                total_edit_size = []
                total_weighted_solution_edits = []
                total_solution_edits = []
                total_weighted_test_edits = []
                total_test_edits = []
                total_weighted_solution_methods = []
                total_solution_methods = []
                total_weighted_test_methods = []
                total_test_methods = []
                total_weighted_launches = []
                total_weighted_test_launches = []
                total_weighted_normal_launches = []
                curr_sizes = {}
                curr_sizes_methods = {}
                if (repr(row['Type']) == repr('Edit') and len(row['Class-Name']) > 0):
                    class_name = repr(row['Class-Name'])
                    curr_size = int(row['Current-Statements'])
                    curr_methods = int(row['Current-Methods'])
                    prev_size = curr_sizes.get(class_name, 0)
                    prev_methods = curr_sizes_methods.get(class_name, 0)

                    edit_size = abs(prev_size - curr_size)
                    method_edit_size = abs(prev_methods - curr_methods)
                    total_weighted_edit_size = [(edit_size * days_to_deadline)]
                    total_edit_size = [edit_size]

                    if (int(row['onTestCase']) == 1):
                        total_weighted_test_edits = [(edit_size * days_to_deadline)]
                        total_test_edits = [ edit_size ]
                        total_weighted_test_methods = [(method_edit_size * days_to_deadline)]
                        total_test_methods = [method_edit_size]
                    else:
                        total_weighted_solution_edits = [(edit_size * days_to_deadline)]
                        total_solution_edits = [edit_size]
                        total_weighted_solution_methods = [(method_edit_size *  days_to_deadline)]
                        total_solution_methods = [method_edit_size]

                    curr_sizes[class_name] = curr_size
                    curr_sizes_methods[class_name] = curr_methods

                elif (repr(row['Type']) == repr('Launch')):
                    total_weighted_launches = [days_to_deadline]

                    if (repr(row['Subtype']) == repr('Test')):
                        total_weighted_test_launches = [days_to_deadline]
                    elif (repr(row['Subtype']) == repr('Normal')):
                        total_weighted_normal_launches = [days_to_deadline]

                prev_row = row

        if (len(total_edit_size) > 0):
            early_often_index = np.sum(total_weighted_edit_size) / np.sum(total_edit_size)
            line_edit_mean = np.mean(total_weighted_edit_size)
            line_edit_sd = np.std(total_weighted_edit_size)
            line_edit_med = np.median(total_weighted_edit_size)
            skewness = (line_edit_mean - line_edit_med) * 3 / line_edit_sd
            solution_stmt_early_often_index = np.sum(total_weighted_solution_edits) / np.sum(total_solution_edits)
            solution_meth_early_often_index = np.sum(total_weighted_solution_methods) / np.sum(total_solution_methods)
            test_stmt_early_often_index = np.sum(total_weighted_test_edits) / np.sum(total_test_edits)
            test_meth_early_often_index = np.sum(total_weighted_test_methods) / np.sum(total_test_methods)
            launch_early_often = np.mean(total_weighted_launches)
            test_launch_early_often = np.mean(total_weighted_test_launches)
            normal_launch_early_often = np.mean(total_weighted_normal_launches)

            to_write = {
                'projectId': prev_row['projectId'],
                'userId': prev_row['userId'],
                'email': prev_row['email'],
                'CASSIGNMENTNAME': prev_row[assignment_field],
                'earlyOftenIndex': early_often_index,
                'lineEditMean': line_edit_mean,
                'lineEditMedian': line_edit_med,
                'lineEditSd': line_edit_sd,
                'skewness': skewness,
                'solutionStmtEarlyOftenIndex': solution_stmt_early_often_index,
                'solutionMethodsEarlyOftenIndex': solution_meth_early_often_index,
                'testStmtsEarlyOftenIndex': test_stmt_early_often_index,
                'testMethodsEarlyOftenIndex': test_meth_early_often_index,
                'launchEarlyOften': launch_early_often,
                'testLaunchEarlyOften': test_launch_early_often,
                'normalLaunchEarlyOften': normal_launch_early_often
            }
            writer.writerow(to_write)

def main(args):
    infile = args[0]
    outfile = args[1]
    deadline = int(args[2])
    try:
        early_often_scores(infile, outfile, deadline)
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Calculates an early/often index for each student project for a given assignment.')
        print('Early/often is the [sum of (editSize * daysToDeadline) / totalEditSize].')
        print('Usage:\n\t./early_often.py <input file> <output file> <assignment deadline as a millisecond timestamp>')
        sys.exit()
    main(sys.argv[1:])
