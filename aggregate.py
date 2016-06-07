#! /usr/bin/env python3

import csv
import numpy as np
import time

def get_sample(project_ids, outfile):
    """
    Gets all raw sensordata for the project_ids in the specified list.

    Keyword arguments:
    outfile -- the file in which to put the sample.
    """
    print("Sampling by projectIds given and putting them in %s..." % (outfile))
    with open('../sensordata.csv', 'r') as fin, open(outfile, 'w') as fout:
        writer = csv.writer(fout, delimiter=',')
        reader = csv.reader(fin, delimiter=',')
        headers = next(reader)
        writer.writerow(headers)
        for row in csv.reader(fin, delimiter=','):
            if (repr(row[0]) in project_ids):
                writer.writerow(row)

def print_distinct(infile, fieldname):
    """
    Prints all distinct values found in given column.

    Keyword arguments:
    infile    -- the input data file (CSV)
    fieldname -- the name of the column.
    """
    values = []
    with open(infile, 'r') as fin:
        for row in csv.DictReader(fin, delimiter=','):
            if (repr(row[fieldname]) not in values):
                values.append(repr(row[fieldname]))

    for thing in values:
        print(thing)

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
        reader = csv.DictReader(fin, delimiter  =',')
        writer = csv.DictWriter(fout, delimiter =',', fieldnames=['projectId', 'userId', 'CASSIGNMENTNAME', 'time', \
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

def get_launch_quartiles(infile, outfile):
    """
    Splits a subsession data file into quartiles based on edits
    per subsession for easier visualisations.

    Keyword arguments:
    infile  -- the name of the file containing subsession data
    outfile -- the name of the file in which to put quartile data
    """
    print('Getting edits-per-launch quartiles...')
    fieldnames = ['workSessionId', 'q1', 'q2', 'q3']

    edit_sizes = []
    prev_row = None


    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        for row in reader:
            prev_row = prev_row or row
            if (row['workSessionId'] == prev_row['workSessionId'] \
                and row['projectId'] == prev_row['projectId']):
                    edit_sizes.append(int(row['editSize']))

                    prev_row = row
            else:
                prev_ws = int(prev_row['workSessionId'])
                a = np.array(edit_sizes)
                low = np.percentile(a, 0)
                q1 = np.percentile(a, 25)
                median = np.percentile(a, 50)
                q3 = np.percentile(a, 75)
                high = np.percentile(a, 100)
                writer.writerow({'workSessionId': prev_ws, 'q1': q1, 'q2': median, 'q3': q3})

                edit_sizes = []
                edit_sizes.append(int(row['editSize']))
                prev_row = row

        prev_ws = int(prev_row['workSessionId'])
        a = np.array(edit_sizes)
        low = np.percentile(a, 0)
        q1 = np.percentile(a, 25)
        median = np.percentile(a, 50)
        q3 = np.percentile(a, 75)
        high = np.percentile(a, 100)
        writer.writerow({'workSessionId': prev_ws, 'q1': q1, 'q2': median, 'q3': q3})

def get_work_sessions(infile, outfile):
    """Collapses subsession data from infile into work session data in outfile."""
    print('Getting work sessions...')

    fieldnames = ['projectId', 'userId', 'assignment', 'workSessionId', 'start_time', 'end_time', 'testLaunches',\
        'normalLaunches', 'editSize', 'editsPerLaunch']

    prev_row = None
    ws = None
    test_launches = 0
    normal_launches = 0
    start_time = None
    edit_size = 0

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        for row in reader:
            prev_row = prev_row or row
            if (row['userId'] == prev_row['userId'] and row['projectId'] == prev_row['projectId'] \
                and row['workSessionId'] == prev_row['workSessionId']):
                    start_time = start_time or int(row['wsStartTime'])
                    edit_size += int(row['editSize'])

                    if (repr(row['launchType']) == repr('Test')):
                        test_launches += 1
                    elif (repr(row['launchType']) == repr('Normal')):
                        normal_launches += 1

                    prev_row = row
            else:
                ratio = edit_size / ((test_launches + normal_launches) or 1)
                writer.writerow({'userId': prev_row['userId'], 'projectId': prev_row['projectId'], \
                    'assignment': prev_row['CASSIGNMENTNAME'], 'workSessionId': prev_row['workSessionId'],\
                    'start_time': start_time, 'end_time': int(prev_row['time']), 'testLaunches': \
                    test_launches, 'normalLaunches': normal_launches, 'editSize': \
                    edit_size, 'editsPerLaunch': ratio })

                edit_size = int(row['editSize'])
                start_time = int(row['wsStartTime'])
                if (repr(row['launchType']) == repr('Test')):
                    test_launches = 1
                    normal_launches = 0
                elif (repr(row['launchType']) == repr('Normal')):
                    normal_launches = 1
                    test_launches = 0
                else:
                    normal_launches = 0
                    test_launches = 0

                prev_row = row

        ratio = edit_size / ((test_launches + normal_launches) or 1)
        writer.writerow({'userId': prev_row['userId'], 'projectId': prev_row['projectId'], \
            'assignment': prev_row['CASSIGNMENTNAME'], 'workSessionId': prev_row['workSessionId'], \
            'start_time': start_time, 'end_time': int(prev_row['time']), 'testLaunches': test_launches, \
            'normalLaunches': normal_launches, 'editSize': edit_size, 'editsPerLaunch': ratio })

def get_time_spent(infile, outfile):
    """
    Takes in worksession data from the infile and gives back
    the time spent on a project for a student.
    """
    print('Getting time spent on project...')
    fieldnames = ['userId', 'projectId', 'assignment', 'timeSpent']

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers to outfile.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        prev_row = None
        time_spent = 0

        for row in reader:
            prev_row = prev_row or row

            if (row['projectId'] == prev_row['projectId'] and row['userId'] == prev_row['userId']):
                time_spent += int(row['end_time']) - int(row['start_time'])
                prev_row = row
            else:
                writer.writerow({'userId': prev_row['userId'], 'projectId': prev_row['projectId'], \
                    'assignment': prev_row['assignment'], 'timeSpent': time_spent / 1080000})
                time_spent = int(row['end_time']) - int(row['start_time'])
                prev_row = row

        writer.writerow({'userId': row['userId'], 'projectId': row['projectId'], 'assignment': row['assignment'],\
            'timeSpent': time_spent / 1080000 })
