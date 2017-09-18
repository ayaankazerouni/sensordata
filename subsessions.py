#! /usr/bin/env python3

import csv
import sys
import traceback
import datetime

def get_subsessions(infile, outfile, threshold=3, cleaned=None):
    """
    Clusters data into work sessions and subsessions.

    Subsessions are separated by launch events. Work sessions
    are separated by a gap of 3 hours without activity.

    Keyword arguments:
    infile  -- the input file (CSV)
    outfile -- the resultant file (CSV)
    """
    print('Getting subsessions...')
    assignment_field = 'CASSIGNMENTNAME'
    if cleaned:
        assignment_field = 'cleaned_assignment'
    fieldnames = [
        'projectId',
        'email',
        'userId',
        'CASSIGNMENTNAME',
        'time',
        'workSessionId',
        'editSizeStmts',
        'testEditSizeStmts',
        'editSizeMethods',
        'testEditSizeMethods',
        'wsStartTime',
        'launchType'
    ]
    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        # Set initial values.
        prev_launch_type = None
        ws_id = 0
        edit_size_stmts = 0
        edit_size_methods = 0
        test_edit_size_stmts = 0
        test_edit_size_methods = 0
        curr_sizes_stmts = {}
        curr_sizes_methods = {}
        test_curr_sizes_stmts = {}
        test_curr_sizes_methods = {}
        ws_start_time = None
        prev_row = None

        for row in reader:
            # Setting prev values to the first row's values
            # to start off with. If prev values are set already,
            # they remain unchanged.
            ws_start_time = ws_start_time or to_int(row['time'])
            prev_row = prev_row or row

            if (row['userId'] != prev_row['userId'] or row[assignment_field] != prev_row[assignment_field]):

                to_write = {
                    'userId': prev_row['userId'],
                    'projectId': prev_row['projectId'],
                    'email': prev_row['email'],
                    'CASSIGNMENTNAME': prev_row[assignment_field],
                    'time': prev_row['time'],
                    'workSessionId': ws_id,
                    'editSizeStmts': edit_size_stmts,
                    'testEditSizeStmts': test_edit_size_stmts,
                    'editSizeMethods': edit_size_methods,
                    'testEditSizeMethods': test_edit_size_methods,
                    'wsStartTime': ws_start_time,
                    'launchType': 'N/A'
                }
                writer.writerow(to_write)

                # Reset persistent values for next user or assignment.
                ws_id = 0
                edit_size_stmts = 0
                edit_size_methods = 0
                test_edit_size_stmts = 0
                test_edit_size_methods = 0
                curr_sizes_stmts = {}
                ws_start_time = to_int(row['time'])
                prev_row = row

            prev_time = datetime.datetime.fromtimestamp(to_int(prev_row['time']) / 1000)
            curr_time = datetime.datetime.fromtimestamp(to_int(row['time']) / 1000)
            hours = (curr_time - prev_time).total_seconds() / 3600
            if (hours < threshold):
                # Within the same work session, we add up numbers for edit sizes
                # and keep track of file sizes.
                if (repr(row['Type']) == repr('Edit')):
                    if(len(row['Class-Name']) > 0):
                        # An edit took place, so we're going to store the current
                        # size of the file (in statements) in a dictionary for
                        # quick lookup the next time this file is edited.
                        class_name = repr(row['Class-Name'])
                        stmts = to_int(row['Current-Statements'])
                        prev_size_stmts = curr_sizes_stmts.get(class_name, 0)

                        if (to_int(row['onTestCase']) == 1):
                            test_edit_size_stmts += abs(stmts - prev_size_stmts)
                        else:
                            edit_size_stmts += abs(stmts - prev_size_stmts)
                        curr_sizes_stmts[class_name] = stmts
                        prev_launch_type = None
                    if(repr(row['Unit-Type']) == repr('Method')\
                        and repr(row['Subsubtype']) in [repr('Add'), repr('Remove')]):
                        if (to_int(row['onTestCase']) == 1):
                            test_edit_size_methods += 1
                        else:
                            edit_size_methods += 1
                        prev_launch_type = None

                elif (repr(row['Type']) == repr('Launch')):
                    # A launch occured, so we break into another 'subsession',
                    # writing out aggregate data and resetting values.
                    launch_type = row['Subtype']
                    if (repr(prev_launch_type) != repr(launch_type)):
                        to_write = {
                            'userId': row['userId'],
                            'projectId': row['projectId'],
                            'email': row['email'],
                            'CASSIGNMENTNAME': row[assignment_field],
                            'time': row['time'],
                            'workSessionId': ws_id,
                            'editSizeStmts': edit_size_stmts,
                            'testEditSizeStmts': test_edit_size_stmts,
                            'editSizeMethods': edit_size_methods,
                            'testEditSizeMethods': test_edit_size_methods,
                            'wsStartTime': ws_start_time,
                            'launchType': launch_type
                        }
                        writer.writerow(to_write)

                        edit_size_stmts = 0
                        edit_size_methods = 0
                        test_edit_size_stmts = 0
                        test_edit_size_methods = 0

                    prev_launch_type = launch_type
            else:
                # Work session ended, so we write out data for the current subsession, with edits
                # that are 'not followed by any launch'
                to_write = {
                    'userId': prev_row['userId'],
                    'projectId': prev_row['projectId'],
                    'email': prev_row['email'],
                    'CASSIGNMENTNAME': prev_row[assignment_field],
                    'time': prev_row['time'],
                    'workSessionId': ws_id,
                    'editSizeStmts': edit_size_stmts,
                    'testEditSizeStmts': test_edit_size_stmts,
                    'editSizeMethods': edit_size_methods,
                    'testEditSizeMethods': test_edit_size_methods,
                    'wsStartTime': ws_start_time,
                    'launchType': 'N/A'
                }
                writer.writerow(to_write)
                ws_id += 1
                edit_size_stmts = 0
                test_edit_size_stmts = 0
                edit_size_methods = 0
                test_edit_size_methods = 0
                ws_start_time = row['time']

            prev_row = row

def to_int(num):
    """
    Converts a string to an integer; can handle
    scientific notation.

    Will throw an exception if string is not an integer in scientific
    notation or otherwise.
    """
    return int(float(num))

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        if len(args) == 3:
            get_subsessions(infile, outfile, args[2])
        else:
            get_subsessions(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)
    except KeyError as e:
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Clusters data into work sessions and subsessions.\n\nSubsessions are separated by ' +
            'launch events. Work sessions are separated by a gap of 3 hours without activity.')
        print('Usage:\n\t./subsessions.py <input_file> <output_file>')
        sys.exit()
    main(sys.argv[1:])
