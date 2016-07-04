#! /usr/bin/env python3

import csv
import sys

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
                    'assignment': prev_row['cleaned_assignment'], 'timeSpent': time_spent / 1080000})
                time_spent = int(row['end_time']) - int(row['start_time'])
                prev_row = row

        writer.writerow({ 'userId': prev_row['userId'], 'projectId': prev_row['projectId'], 'assignment':\
            prev_row['cleaned_assignment'], 'timeSpent': time_spent / 1080000 })

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        get_time_spent(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File %s does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Takes in worksession data from the infile and gives back the time spent on a project for a student.')
        print('Usage:\n\t./time_spent.py [input_file] [output_file]')
        sys.exit()
    main(sys.argv[1:])
