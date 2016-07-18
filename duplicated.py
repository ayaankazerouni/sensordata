#! /usr/bin/env python3

import csv
import sys

def get_duplicated(infile, outfile):
    """
    Prints out data from import events that appear twice for the same
    userId, projectId, and timestamp, resulting a list of student projects
    that may have duplicated data.

    Keyword arguments:
    infile  -- the input file (CSV)
    outfile -- the output file (CSV)
    """
    print('Getting duplicated projects...')
    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        fieldnames = ['userId', 'projectId', 'time', 'uri', 'subtype']
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        # Set initial values
        prev_row = None

        # Store will have structure like this:
        # {
        #     userId: {
        #         projectId: {
        #             [ list of timestamps of import events ]
        #         }
        #     }
        # }
        store = {}
        written = {}

        for row in reader:
            if repr(row['Subtype']) == repr('Import'):
                user_id = row['userId']
                project_id = row['projectId']
                time = row['time']
                subtype = row['Subtype']
                uri = row['uri']

                if time not in store.get(user_id, {}).get(project_id, []):
                    store.setdefault(user_id, {}).setdefault(project_id, []).append(time)
                else:
                    if time not in written.get(user_id, {}).get(project_id, []):
                        writer.writerow({ 'userId': user_id, 'projectId': project_id, 'time': time, 'uri': uri, \
                            'subtype': subtype })
                        written.setdefault(user_id, {}).setdefault(project_id, []).append(time)

def get_duplicated_from_time_spent(infile, outfile):
    """
    Prints out the userId and projectId for projects
    that appear twice with the same data in a time_spent.csv
    file.
    """
    print('Getting duplicates from the time_spent file...')
    fieldnames = [ 'userId', 'projectId' ]

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers to outfile.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        prev_row = None
        start = True
        written = {}

        for row in reader:
            user_id = row['userId']
            project_id = row['projectId']

            if start:
                prev_row = row
                start = False
            elif row == prev_row and project_id not in written.get(user_id, []):
                writer.writerow({ 'userId': user_id, 'projectId': project_id })
                written.setdefault(user_id, []).append(project_id)

            prev_row = row

def main(args):
    method = args[0]
    infile = args[1]
    outfile = args[2]
    try:
        if method == 'raw':
            get_duplicated(infile, outfile)
        elif method == 'time':
            get_duplicated_from_time_spent(infile, outfile)
        else:
            print_usage()
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)

def print_usage():
    print("Get userId, projectId, uri, time, and Subtype for projects where " +
        " an Import event occurs at the same timestamp.")
    print("Usage:\n./duplicated.py <raw | time> <input_file> <output_file>")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print_usage()
        sys.exit()
    main(sys.argv[1:])
