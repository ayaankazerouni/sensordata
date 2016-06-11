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
            'workSessionId', 'editSize', 'launchType', 'wsStartTime'])

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        prev_launch_type = None
        ws_id = 0
        subs_edit_size = 0
        file_sizes = {}
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
                    'editSize': subs_edit_size, 'launchType': 'N/A', 'wsStartTime': ws_start_time })

                ws_id = 0
                subs_edit_size = 0
                file_sizes = {}
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
                    prev_size = file_sizes.get(class_name, 0)
                    subs_edit_size += abs(stmts - prev_size)
                    file_sizes[class_name] = stmts
                    prev_launch_type = None

                elif (repr(row['Type']) == repr('Launch')):
                    # A launch occured, so we break into another 'subsession',
                    # writing out aggregate data and resetting values.
                    launch_type = row['LaunchType']
                    if (repr(prev_launch_type) != repr(launch_type)):
                        writer.writerow({'userId': row['userId'], 'projectId': row['projectId'], 'CASSIGNMENTNAME': \
                            row['CASSIGNMENTNAME'], 'time': row['time'], 'workSessionId': ws_id, 'editSize': \
                            subs_edit_size, 'launchType': launch_type, 'wsStartTime': ws_start_time })
                        subs_edit_size = 0
                        file_sizes = {}
                    prev_launch_type = launch_type
            else:
                # Work session ended, so we write out data for the current subsession, with edits
                # that are 'not followed by any launch'
                writer.writerow({'userId': prev_row['userId'], 'projectId': prev_row['projectId'], \
                    'CASSIGNMENTNAME': row['CASSIGNMENTNAME'], 'time': prev_row['time'], 'workSessionId': ws_id, \
                    'editSize': subs_edit_size, 'launchType': 'N/A', 'wsStartTime': ws_start_time })
                ws_id += 1
                subs_edit_size = 0
                file_sizes = {}
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
