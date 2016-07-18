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

        # Cache will have structure like this:
        # {
        #     userId: {
        #         projectId: {
        #             import event with timestamp
        #         }
        #     }
        # }
        cache = {}

        for row in reader:
            if repr(row['Subtype']) == repr('Import'):
                user_id = row['userId']
                project_id = row['projectId']
                time = row['time']
                subtype = row['Subtype']
                uri = row['uri']

                if user_id in cache:
                    if project_id in cache[user_id]:
                        if time in cache[user_id][project_id]:
                            writer.writerow({ 'userId': user_id, 'projectId': project_id, 'time': time, 'uri': uri, \
                                'subtype': subtype })
                        else:
                            cache[user_id][project_id].append(time)
                    else:
                        times = [ time ]
                        cache[user_id][project_id] = times
                else:
                    cache[user_id] = {}
                    cache[user_id][project_id] = [ time ]

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        get_duplicated(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)

def print_usage():
    print("Get userId, projectId, uri, time, and Subtype for projects where " +
        " an Import event occurs at the same timestamp.")
    print("Usage: ./duplicated.py <input_file> <output_file>")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit()
    main(sys.argv[1:])
