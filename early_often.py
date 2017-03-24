#! /usr/bin/env python3

import sys
import csv
import datetime

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
        'solutionStmtEarlyOftenIndex',
        'solutionMethodsEarlyOftenIndex',
        'testStmtsEarlyOftenIndex',
        'testMethodsEarlyOftenIndex'
    ]

    due_date = datetime.date.fromtimestamp(deadline / 1000)

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

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
                prev_row = row
            else:
                if (total_edit_size > 0):
                    early_often_index = total_weighted_edit_size / total_edit_size
                    solution_stmt_early_often_index = total_weighted_solution_edits / total_solution_edits
                    solution_meth_early_often_index = total_weighted_solution_methods / total_solution_methods
                    test_stmt_early_often_index = total_weighted_test_edits / total_test_edits
                    test_meth_early_often_index = total_weighted_test_methods / total_test_methods

                    to_write = {
                        'projectId': prev_row['projectId'],
                        'userId': prev_row['userId'],
                        'email': prev_row['email'],
                        'CASSIGNMENTNAME': prev_row['CASSIGNMENTNAME'],
                        'earlyOftenIndex': early_often_index,
                        'solutionStmtEarlyOftenIndex': solution_stmt_early_often_index,
                        'solutionMethodsEarlyOftenIndex': solution_meth_early_often_index,
                        'testStmtsEarlyOftenIndex': test_stmt_early_often_index,
                        'testMethodsEarlyOftenIndex': test_meth_early_often_index
                    }
                    writer.writerow(to_write)

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
                    total_weighted_edit_size = (edit_size * days_to_deadline)

                    if (int(row['onTestCase']) == 1):
                        total_weighted_test_edits = (edit_size * days_to_deadline)
                        total_test_edits = edit_size
                        total_weighted_test_methods = (method_edit_size * days_to_deadline)
                        total_test_methods = method_edit_size
                    else:
                        total_weighted_solution_edits = (edit_size * days_to_deadline)
                        total_solution_edits = edit_size
                        total_weighted_solution_methods = (method_edit_size *  days_to_deadline)
                        total_solution_methods = method_edit_size

                    total_edit_size = edit_size
                    curr_sizes[class_name] = curr_size
                    curr_sizes_methods[class_name] = curr_methods

                prev_row = row

        if (total_edit_size > 0):
            early_often_index = total_weighted_edit_size / total_edit_size
            solution_stmt_early_often_index = total_weighted_solution_edits / total_solution_edits
            solution_meth_early_often_index = total_weighted_solution_methods / total_solution_methods
            test_stmt_early_often_index = total_weighted_test_edits / total_test_edits
            test_meth_early_often_index = total_weighted_test_methods / total_test_methods

            to_write = {
                'projectId': prev_row['projectId'],
                'userId': prev_row['userId'],
                'email': prev_row['email'],
                'CASSIGNMENTNAME': prev_row['CASSIGNMENTNAME'],
                'earlyOftenIndex': early_often_index,
                'solutionStmtEarlyOftenIndex': solution_stmt_early_often_index,
                'solutionMethodsEarlyOftenIndex': solution_meth_early_often_index,
                'testStmtsEarlyOftenIndex': test_stmt_early_often_index,
                'testMethodsEarlyOftenIndex': test_meth_early_often_index
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
