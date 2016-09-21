#! /usr/bin/env python3

import csv
import sys
import datetime
import numpy as np

def incremental_checking(infile, outfile):
    """
    Calculates metrics for 'incremental checking'.

    * Average solution edit size weighted by the time (in hours) until the next
        launch (of any kind)
    * Average solution edit size weighted by the time (in hours) until the next test launch
    * Average test edit size weighted by the time (in hours) until the next test launch

    Keyword arguments:
    infile  -- the input file (cleaned CSV sensordata)
    outfile -- the resultant file (CSV)
    """
    fieldnames = [
        'projectId',
        'userId',
        'cleaned_assignment',
        'solutionEditAnyLaunch',
        'solutionEditRegularLaunch',
        'solutionEditTestLaunch',
        'testEditTestLaunch'
    ]

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        # The size of each edit (weighted by time until the next appropriate launch)
        weighted_sol_edit_any_launch = []
        weighted_sol_edit_reg_launch = []
        weighted_sol_edit_test_launch = []
        weighted_test_edit_test_launch = []

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

            if (row['userId'] == prev_row['userId'] and row['projectId'] == prev_row['projectId']):
                if (repr(row['Type']) == repr('Edit')):
                    if (len(row['Class-Name']) > 0):
                        class_name = repr(row['Class-Name'])
                        stmts = int(row['Current-Statements'])
                        prev_size = curr_sizes.get(class_name, 0)
                        curr_sizes[class_name] = stmts

                        edit_size = abs(stmts - prev_size)
                        time = int(row['time'])
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
                    launch_time = int(row['time'])

                    # solution edits by launches of any kind
                    for edit in solution_edits_per_any_launch:
                        edit_time = edit['time']
                        size = edit['size']

                        hours = get_diff_in_hours(edit_time, launch_time)
                        weighted_sol_edit_any_launch.append(size * hours)
                    if not solution_edits_per_any_launch:
                        weighted_sol_edit_any_launch.append(0)
                    solution_edits_per_any_launch = []

                    if (repr(launch_type) == repr('Test')):
                        for edit in solution_edits_per_test_launch:
                            edit_time = edit['time']
                            size = edit['size']

                            hours = get_diff_in_hours(edit_time, launch_time)
                            weighted_sol_edit_test_launch.append(size * hours)
                        if not solution_edits_per_test_launch:
                            weighted_sol_edit_test_launch.append(0)
                        solution_edits_per_test_launch = []

                        for edit in test_edits_per_test_launch:
                            edit_time = edit['time']
                            size = edit['size']

                            hours = get_diff_in_hours(edit_time, launch_time)
                            weighted_test_edit_test_launch.append(size * hours)
                        if not test_edits_per_test_launch:
                            weighted_test_edit_test_launch.append(0)
                        test_edits_per_test_launch = []
                    else:
                        for edit in solution_edits_per_reg_launch:
                            edit_time = edit['time']
                            size = edit['size']

                            hours = get_diff_in_hours(edit_time, launch_time)
                            weighted_sol_edit_reg_launch.append(size * hours)
                        if not solution_edits_per_reg_launch:
                            weighted_sol_edit_reg_launch.append(0)
                        solution_edits_per_reg_launch = []

                prev_row = row
            else:
                a_solution_any = np.array(weighted_sol_edit_any_launch)
                a_solution_regular = np.array(weighted_sol_edit_reg_launch)
                a_test_test = np.array(weighted_test_edit_test_launch)
                a_solution_test = np.array(weighted_sol_edit_test_launch)

                mean_solution_any = np.mean(a_solution_any) if (len(weighted_sol_edit_any_launch) > 0) else 9999
                mean_solution_regular = np.mean(a_solution_regular) if (len(weighted_sol_edit_reg_launch) > 0) else 9999
                mean_solution_test = np.mean(a_solution_test) if (len(weighted_sol_edit_test_launch) > 0) else 9999
                mean_test_test = np.mean(a_test_test) if (len(weighted_test_edit_test_launch) > 0) else 9999

                to_write = {
                    'projectId': prev_row['projectId'],
                    'userId': prev_row['userId'],
                    'cleaned_assignment': prev_row['cleaned_assignment'],
                    'solutionEditAnyLaunch': mean_solution_any,
                    'solutionEditRegularLaunch': mean_solution_regular,
                    'solutionEditTestLaunch': mean_solution_test,
                    'testEditTestLaunch': mean_test_test
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

            mean_solution_any = np.mean(a_solution_any) if (len(weighted_sol_edit_any_launch) > 0) else 9999
            mean_solution_regular = np.mean(a_solution_regular) if (len(weighted_sol_edit_reg_launch) > 0) else 9999
            mean_solution_test = np.mean(a_solution_test) if (len(weighted_sol_edit_test_launch) > 0) else 9999
            mean_test_test = np.mean(a_test_test) if (len(weighted_test_edit_test_launch) > 0) else 9999

            to_write = {
                'projectId': prev_row['projectId'],
                'userId': prev_row['userId'],
                'cleaned_assignment': prev_row['cleaned_assignment'],
                'solutionEditAnyLaunch': mean_solution_any,
                'solutionEditRegularLaunch': mean_solution_regular,
                'solutionEditTestLaunch': mean_solution_test,
                'testEditTestLaunch': mean_test_test
            }

            writer.writerow(to_write)

def get_diff_in_hours(timestamp1, timestamp2):
    time1 = datetime.datetime.fromtimestamp(timestamp1 / 1000)
    time2 = datetime.datetime.fromtimestamp(timestamp2 / 1000)

    delta = (time2 - time1).total_seconds()
    if(delta < 0):
        print(time1)
        print(time2)
        print('-------')
    hours = delta / 3600

    return hours

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        incremental_checking(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)
    except KeyError as e:
        cause = e.args[0]
        if (cause == 'cleaned_assignment'):
            print("Key Error! Are you using a cleaned data file? Please run ./clean.py on the data file and use " +
                "the resulting file as input.")
        else:
            traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Gets incremental checking scores for users. Requires cleaned sensordata as input.')
        print('Usage:\n\t./incremental_checking.py <input file> <output file>')
        sys.exit()
    main(sys.argv[1:])
