#! /usr/bin/env python3

import sys
import csv
import datetime

def early_often_scores(infile, outfile, deadline):
    fieldnames = [
        'projectId',
        'userId',
        'cleaned_assignment',
        'earlyOftenIndex',
        'testSolutionEditIndex',
        'testSolutionMethodsIndex'
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
        total_weighted_test_edits = 0
        total_weighted_solution_methods = 0
        total_weighted_test_methods = 0

        curr_sizes = {}
        curr_sizes_methods = {}

        for row in reader:
            prev_row = prev_row or row

            time = int(row['time'])
            date = datetime.date.fromtimestamp(time / 1000)
            days_to_deadline = (due_date - date).days

            if (row['userId'] == prev_row['userId'] and row['projectId'] == prev_row['projectId']):
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
                        total_weighted_test_methods += (method_edit_size * days_to_deadline)
                    else:
                        total_weighted_solution_edits += (edit_size * days_to_deadline)
                        total_weighted_solution_methods += (method_edit_size *  days_to_deadline)

                    curr_sizes[class_name] = curr_size
                    curr_sizes_methods[class_name] = curr_methods
                prev_row = row
            else:
                if (total_edit_size > 0):
                    early_often_index = total_weighted_edit_size / total_edit_size
                    if  (total_weighted_solution_edits > 0):
                        test_solution_edit_index = total_weighted_test_edits / total_weighted_solution_edits
                    else:
                        test_solution_edit_index = 'nan'
                    if (total_weighted_solution_methods > 0):
                        test_solution_methods_index = total_weighted_test_methods / total_weighted_solution_methods
                    else:
                        test_solution_methods_index = 'nan'
                    to_write = {
                        'projectId': prev_row['projectId'],
                        'userId': prev_row['userId'],
                        'cleaned_assignment': prev_row['cleaned_assignment'],
                        'earlyOftenIndex': early_often_index,
                        'testSolutionEditIndex': test_solution_edit_index,
                        'testSolutionMethodsIndex': test_solution_methods_index
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
                        total_weighted_test_methods = (method_edit_size * days_to_deadline)
                    else:
                        total_weighted_solution_edits = (edit_size * days_to_deadline)
                        total_weighted_solution_methods = (method_edit_size * days_to_deadline)

                    total_edit_size = edit_size
                    curr_sizes[class_name] = curr_size
                    curr_sizes_methods[class_name] = curr_methods

                prev_row = row

        if (total_edit_size > 0):
            early_often_index = total_weighted_edit_size / total_edit_size
            if  (total_weighted_solution_edits > 0):
                test_solution_edit_index = total_weighted_test_edits / total_weighted_solution_edits
            else:
                test_solution_edit_index = 'nan'
            if (total_weighted_solution_methods > 0):
                test_solution_methods_index = total_weighted_test_methods / total_weighted_solution_methods
            else:
                test_solution_methods_index = 'nan'
            to_write = {
                'projectId': prev_row['projectId'],
                'userId': prev_row['userId'],
                'cleaned_assignment': prev_row['cleaned_assignment'],
                'earlyOftenIndex': early_often_index,
                'testSolutionEditIndex': test_solution_edit_index,
                'testSolutionMethodsIndex': test_solution_methods_index
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
