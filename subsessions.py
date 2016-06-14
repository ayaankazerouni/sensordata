#! /usr/bin/env python3

import csv
import sys

def get_subsessions(infile, outfile):
    """
    Clusters data into work sessions and subsessions.

    Subsessions are separated by launch events. Work sessions
    are separated by a gap of 3 hours without activity.

    Keyword arguments:
    infile  -- the input file (CSV)
    outfile -- the resultant file (CSV)
    """
    print('Getting subsessions...')
    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=['projectId', 'userId', 'CASSIGNMENTNAME', 'time', \
            'workSessionId', 'editSizeStmts', 'testEditSizeStmts', 'editSizeMethods', 'testEditSizeMethods', \
            'launchType', 'wsStartTime'])

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        # Set initial values.
        prev_launch_type = None
        ws_id = 0
        edit_size_stmts = 0
        edit_size_methods = 0
        test_edit_size_stmts = 0
        test_edit_size_methods = 0
        file_sizes_stmts = {}
        file_sizes_methods = {}
        test_file_sizes_stmts = {}
        test_file_sizes_methods = {}
        ws_start_time = None
        prev_row = None

        for row in reader:
            # Setting prev values to the first row's values
            # to start off with. If prev values are set already,
            # they remain unchanged.
            ws_start_time = ws_start_time or int(row['time'])
            prev_row = prev_row or row

            if (row['userId'] != prev_row['userId'] or row['projectId'] != prev_row['projectId']):
                # Started events for the next user or assignment, so write out aggregate data of prev user
                # before continuing.
                writer.writerow({'userId': prev_row['userId'], 'projectId': prev_row['projectId'], 'CASSIGNMENTNAME': \
                    prev_row['CASSIGNMENTNAME'], 'time': prev_row['time'], 'workSessionId': ws_id, \
                    'editSizeStmts': edit_size_stmts, 'testEditSizeStmts': test_edit_size_stmts, 'editSizeMethods': \
                    edit_size_methods, 'testEditSizeMethods': test_edit_size_methods, 'launchType': 'N/A',\
                    'wsStartTime': ws_start_time })

                # Reset persistent values for next user or assignment.
                ws_id = 0
                edit_size_stmts = 0
                edit_size_methods = 0
                test_edit_size_stmts = 0
                test_edit_size_methods = 0
                file_sizes_stmts = {}
                file_sizes_methods = {}
                test_file_sizes_stmts = {}
                test_file_sizes_methods = {}
                ws_start_time = int(row['time'])
                prev_row = row

            if (abs(int(row['time']) - int(prev_row['time'])) < 10800000):
                # Within the same work session, we add up numbers for edit sizes
                # and keep track of file sizes.
                if (repr(row['Type']) == repr('Edit') and len(row['Class-Name']) > 0):
                    # An edit took place, we we're going to store the current
                    # size of the file (in statements) in a dictionary for
                    # quick lookup the next time this file is edited.
                    class_name = repr(row['Class-Name'])
                    stmts = int(row['Current-Statements'])
                    methods = int(row['Current-Methods'])

                    if (int(row['onTestCase']) == 1):
                        test_prev_size_stmts = test_file_sizes_stmts.get(class_name, 0)
                        test_edit_size_stmts += abs(stmts - test_prev_size_stmts)
                        test_file_sizes_stmts[class_name] = stmts
                        test_prev_size_methods = test_file_sizes_methods.get(class_name, 0)
                        test_edit_size_methods += abs(methods - test_prev_size_methods)
                        test_file_sizes_methods[class_name] = methods
                    else:
                        prev_size_stmts = file_sizes_stmts.get(class_name, 0)
                        edit_size_stmts += abs(stmts - prev_size_stmts)
                        file_sizes_stmts[class_name] = stmts
                        prev_size_methods = file_sizes_methods.get(class_name, 0)
                        edit_size_methods += abs(methods - prev_size_methods)
                        file_sizes_methods[class_name] = methods
                        prev_launch_type = None

                elif (repr(row['Type']) == repr('Launch')):
                    # A launch occured, so we break into another 'subsession',
                    # writing out aggregate data and resetting values.
                    launch_type = row['LaunchType']
                    if (repr(prev_launch_type) != repr(launch_type)):
                        writer.writerow({'userId': row['userId'], 'projectId': row['projectId'], 'CASSIGNMENTNAME': \
                            row['CASSIGNMENTNAME'], 'time': row['time'], 'workSessionId': ws_id, 'editSizeStmts': \
                            edit_size_stmts, 'testEditSizeStmts': test_edit_size_stmts, 'editSizeMethods': \
                            edit_size_methods, 'testEditSizeMethods': test_edit_size_methods, 'launchType': \
                            launch_type, 'wsStartTime': ws_start_time })

                        edit_size_stmts = 0
                        edit_size_methods = 0
                        test_edit_size_stmts = 0
                        test_edit_size_methods = 0
                        file_sizes_stmts = {}
                        file_sizes_methods = {}
                        test_file_sizes_stmts = {}
                        test_file_sizes_methods = {}
                    prev_launch_type = launch_type
            else:
                # Work session ended, so we write out data for the current subsession, with edits
                # that are 'not followed by any launch'
                writer.writerow({ 'userId': prev_row['userId'], 'projectId': prev_row['projectId'], \
                    'CASSIGNMENTNAME': row['CASSIGNMENTNAME'], 'time': prev_row['time'], 'workSessionId': ws_id, \
                    'editSizeStmts': edit_size_stmts, 'testEditSizeStmts': test_edit_size_stmts, 'editSizeMethods': \
                    edit_size_methods, 'testEditSizeMethods': test_edit_size_methods, 'launchType': 'N/A',\
                    'wsStartTime': ws_start_time })
                ws_id += 1
                edit_size_stmts = 0
                edit_size_methods = 0
                file_sizes_stmts = {}
                file_sizes_methods = {}
                ws_start_time = row['time']

            prev_row = row

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        get_subsessions(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File %s does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Clusters data into work sessions and subsessions.\n\nSubsessions are separated by ' +
            'launch events. Work sessions are separated by a gap of 3 hours without activity.')
        print('Usage:\n\t./subsessions.py [input_file] [output_file]')
        sys.exit()
    main(sys.argv[1:])
