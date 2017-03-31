#! /usr/bin/env python3

import csv
import sys
import datetime

def get_time_spent(infile, outfile, deadline = None):
    """
    Takes in worksession data from the infile and gives back
    the time spent on a project for a student.
    """
    print('Getting time spent on project...')
    fieldnames = ['userId', 'email', 'projectId', 'assignment', 'hoursOnProject', 'projectStartTime']

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers to outfile.
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        prev_row = None
        time_spent = 0
        project_start_time = None

        for row in reader:
            if deadline:
                current = datetime.date.fromtimestamp(int(float(row['start_time'])) / 1000)
                due_date = datetime.date.fromtimestamp(int(float(deadline)) / 1000)
                days_to_deadline = (due_date - current).days

                if days_to_deadline < -4:
                    prev_row = row
                    continue

            prev_row = prev_row or row

            if (row['CASSIGNMENTNAME'] == prev_row['CASSIGNMENTNAME'] and row['userId'] == prev_row['userId']):
                project_start_time = project_start_time or int(float(row['start_time']))
                start_time = datetime.datetime.fromtimestamp(int(float(row['start_time'])) / 1000)
                end_time = datetime.datetime.fromtimestamp(int(float(row['end_time'])) / 1000)
                hours = (end_time - start_time).total_seconds() / 3600
                time_spent += hours
            else:
                writer.writerow({'userId': prev_row['userId'], 'email': prev_row['email'],
                    'projectId': prev_row['projectId'], 'assignment': prev_row['CASSIGNMENTNAME'],
                    'hoursOnProject': time_spent, 'projectStartTime': project_start_time})
                end_time = datetime.datetime.fromtimestamp(int(float(row['end_time'])) / 1000)
                start_time = datetime.datetime.fromtimestamp(int(float(row['start_time'])) / 1000)
                project_start_time = int(float(row['start_time']))
                time_spent = (end_time - start_time).total_seconds() / 3600

            prev_row = row

        writer.writerow({ 'userId': prev_row['userId'],
            'email': prev_row['email'],
            'projectId': prev_row['projectId'],
            'assignment': prev_row['CASSIGNMENTNAME'],
            'hoursOnProject': time_spent,
            'projectStartTime': project_start_time
        })

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
        print('Usage:\n\t./time_spent.py <input_file> <output_file>')
        sys.exit()
    main(sys.argv[1:])
