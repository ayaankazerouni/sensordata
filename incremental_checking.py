"""
Calculates incremental checking metrics: mean
amounts of [solution/test] code written between successive
[solution/test] launches.

(These measures didn't return anything interesting)
"""

#! /usr/bin/env python3

import csv
import sys
import datetime
import numpy as np

def incremental_checking(infile, outfile, deadline = None):
    """
    Calculates metrics for 'incremental checking'.

    * Average solution edit size weighted by the time (in hours) until the next
        launch (of any kind)
    * Average solution edit size weighted by the time (in hours) until the next test launch
    * Average test edit size weighted by the time (in hours) until the next test launch

    Args:
    infile (str): path to the input file (CSV)
    outfile (str): path to the resultant file (CSV)
    """
    fieldnames = [
        'projectId',
        'userId',
        'email',
        'CASSIGNMENTNAME',
        'solutionEditAnyLaunch',
        'solutionEditRegularLaunch',
        'solutionEditTestLaunch',
        'testEditTestLaunch',
        'testEditPerSolutionEdit'
    ]

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        headers = next(reader)
        assignment_field = 'CASSIGNMENTNAME'
        if 'cleaned_assignment' in headers.keys():
            assignment_field = 'cleaned_assignment'

        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        # The size of each edit (weighted by time until the next appropriate launch)
        weighted_sol_edit_any_launch = []
        weighted_sol_edit_reg_launch = []
        weighted_sol_edit_test_launch = []
        weighted_test_edit_test_launch = []
        weighted_test_per_solution_edits = []

        # Each edit has the format
        # {
        #   size: [int]
        #   time: [unix ms timestamp]
        # }
        solution_edits_per_test_launch = []
        solution_edits_per_reg_launch = []
        test_edits_per_test_launch = []
        solution_edits_per_any_launch = []

        prev_row = None
        curr_sizes = {}

        for row in reader:
            prev_row = prev_row or row

            if deadline:
                due_date = datetime.date.fromtimestamp(int(float(deadline)) / 1000)
                time = int(float(row['time']))
                event_date = datetime.date.fromtimestamp(time / 1000)
                days_to_deadline  = (due_date - event_date).days
                if days_to_deadline < - 4:
                    prev_row = row
                    continue

            if (row['userId'] == prev_row['userId']):
                if (repr(row['Type']) == repr('Edit')):
                    if (len(row['Class-Name']) > 0):
                        class_name = repr(row['Class-Name'])
                        stmts = int(row['Current-Statements'])
                        prev_size = curr_sizes.get(class_name, 0)
                        curr_sizes[class_name] = stmts

                        edit_size = abs(stmts - prev_size)
                        time = int(float(row['time']))
                        edit = {
                            'size': edit_size,
                            'time': time
                        }

                        if(int(row['onTestCase']) == 1):
                            test_edits_per_test_launch.append(edit)
                        else:
                            solution_edits_per_any_launch.append(edit)
                            solution_edits_per_test_launch.append(edit)
                            solution_edits_per_reg_launch.append(edit)

                elif (repr(row['Type']) == repr('Launch')):
                    launch_type = row['Subtype']
                    launch_time = int(float(row['time']))

                    # solution edits by launches of any kind
                    for edit in solution_edits_per_any_launch:
                        edit_time = edit['time']
                        size = edit['size']

                        hours = get_diff_in_hours(edit_time, launch_time)
                        weighted_sol_edit_any_launch.append(size * hours)
                    solution_edits_per_any_launch = []

                    if (repr(launch_type) == repr('Test')):
                        total_solution_edit_per_test_launch = 0
                        total_test_edit_per_test_launch = 0

                        for edit in solution_edits_per_test_launch:
                            edit_time = edit['time']
                            size = edit['size']

                            hours = get_diff_in_hours(edit_time, launch_time)
                            weighted_sol_edit_test_launch.append(size * hours)
                            total_solution_edit_per_test_launch += size * hours
                        solution_edits_per_test_launch = []

                        for edit in test_edits_per_test_launch:
                            edit_time = edit['time']
                            size = edit['size']

                            hours = get_diff_in_hours(edit_time, launch_time)
                            weighted_test_edit_test_launch.append(size * hours)
                            total_test_edit_per_test_launch += size * hours
                        test_edits_per_test_launch = []

                        if total_solution_edit_per_test_launch > 0:
                            test_edits_per_solution_edits = total_test_edit_per_test_launch / total_solution_edit_per_test_launch
                            weighted_test_per_solution_edits.append(test_edits_per_solution_edits)
                    else:
                        for edit in solution_edits_per_reg_launch:
                            edit_time = edit['time']
                            size = edit['size']

                            hours = get_diff_in_hours(edit_time, launch_time)
                            weighted_sol_edit_reg_launch.append(size * hours)
                        solution_edits_per_reg_launch = []

                prev_row = row
            else:
                a_solution_any = np.array(weighted_sol_edit_any_launch)
                a_solution_regular = np.array(weighted_sol_edit_reg_launch)
                a_test_test = np.array(weighted_test_edit_test_launch)
                a_solution_test = np.array(weighted_sol_edit_test_launch)
                a_test_per_solution_edits = np.array(weighted_test_per_solution_edits)

                mean_solution_any = np.mean(a_solution_any)
                mean_solution_regular = np.mean(a_solution_regular)
                mean_solution_test = np.mean(a_solution_test)
                mean_test_test = np.mean(a_test_test)
                mean_test_per_solution_edits = np.mean(a_test_per_solution_edits)

                to_write = {
                    'projectId': prev_row['projectId'],
                    'userId': prev_row['userId'],
                    'email': prev_row['email'],
                    'CASSIGNMENTNAME': prev_row[assignment_field],
                    'solutionEditAnyLaunch': mean_solution_any,
                    'solutionEditRegularLaunch': mean_solution_regular,
                    'solutionEditTestLaunch': mean_solution_test,
                    'testEditTestLaunch': mean_test_test,
                    'testEditPerSolutionEdit': mean_test_per_solution_edits
                }

                writer.writerow(to_write)

                solution_edits_per_any_launch = []
                solution_edits_per_reg_launch = []
                solution_edits_per_test_launch = []
                test_edits_per_test_launch = []
                weighted_sol_edit_test_launch = []
                weighted_sol_edit_reg_launch = []
                weighted_test_edit_test_launch = []
                weighted_sol_edit_any_launch = []
                prev_row = row
                curr_sizes = {}
        else:
            a_solution_any = np.array(weighted_sol_edit_any_launch)
            a_solution_regular = np.array(weighted_sol_edit_reg_launch)
            a_test_test = np.array(weighted_test_edit_test_launch)
            a_solution_test = np.array(weighted_sol_edit_test_launch)
            a_test_per_solution_edits = np.array(weighted_test_per_solution_edits)

            mean_solution_any = np.mean(a_solution_any)
            mean_solution_regular = np.mean(a_solution_regular)
            mean_solution_test = np.mean(a_solution_test)
            mean_test_test = np.mean(a_test_test)
            mean_test_per_solution_edits = np.mean(a_test_per_solution_edits)

            to_write = {
                'projectId': prev_row['projectId'],
                'userId': prev_row['userId'],
                'email': prev_row['email'],
                'CASSIGNMENTNAME': prev_row[assignment_field],
                'solutionEditAnyLaunch': mean_solution_any,
                'solutionEditRegularLaunch': mean_solution_regular,
                'solutionEditTestLaunch': mean_solution_test,
                'testEditTestLaunch': mean_test_test,
                'testEditPerSolutionEdit': mean_test_per_solution_edits
            }

            writer.writerow(to_write)

def get_diff_in_hours(timestamp1, timestamp2):
    time1 = datetime.datetime.fromtimestamp(timestamp1 / 1000)
    time2 = datetime.datetime.fromtimestamp(timestamp2 / 1000)

    delta = (time2 - time1).total_seconds()
    hours = delta / 3600

    return hours

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        if len(args) == 3:
            incremental_checking(infile, outfile, args[2])
        else:
            incremental_checking(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Gets incremental checking scores for users. Requires cleaned sensordata as input.')
        print('Usage:\n\t./incremental_checking.py <input file> <output file>')
        sys.exit()
    main(sys.argv[1:])
