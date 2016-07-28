#! /usr/bin/env python3

import csv
import sys
import re

def clean_assignment_names(infile, outfile):
    """
    Assigns cleaned assignment names to each row, making an educated guess
    by looking at the URI for that sensordata event.

    Keyword arguments:
    infile  -- the file containing the unclean sensordata
    outfile -- the file containing the clean sensordata, with an added
        column 'cleaned_assignment'. This column is used for other aggregation
        operations (subsessions, work_sessions, etc.).
    """
    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        headers = list((fn) for fn in reader.fieldnames)
        headers.append('milestone1')
        headers.append('milestone2')
        headers.append('milestone3')
        headers.append('earlyBonus')
        headers.append('dueTime')
        headers.append('cleaned_assignment')
        headers.append('cleaned?')
        headers.remove('LaunchType')
        headers.remove('TerminationType')

        writer = csv.DictWriter(fout, delimiter=',', fieldnames=headers)

        # Write headers first
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

        assignment_name = None
        for row in reader:
            assignment_name = squashed_assignment_name(row['CASSIGNMENTNAME'])
            uri = row['uri']
            project_id = row['projectId']
            project_dir = project_dir_from_uri(uri)

            if project_dir is None:
                row['cleaned_assignment'] = assignment_name
                row['cleaned?'] = 0
            elif assignment_name != project_dir:
                assignment_name = project_dir
                row['cleaned_assignment'] = project_dir
                row['cleaned?'] = 1
            else:
                row['cleaned_assignment'] = assignment_name
                row['cleaned?'] = 1

            # Storing the due time for each assignment
            if assignment_name == 'Assignment 1':
                row['milestone1'] = 1453849200000
                row['milestone2'] = 1454367600000
                row['milestone3'] = 1454540400000
                row['earlyBonus'] = 1455058800000
                row['dueTime'] = 1455145200000
            elif assignment_name == 'Assignment 2':
                row['milestone1'] = 1455922800000
                row['milestone2'] = 1456614000000
                row['milestone3'] = 1457391600000
                row['earlyBonus'] = 1458082800000
                row['dueTime'] = 1458169200000
            elif assignment_name == 'Assignment 3':
                row['milestone1'] = -1
                row['milestone2'] = -1
                row['milestone3'] = -1
                row['earlyBonus'] = 1459994400000
                row['dueTime'] = 1460080800000
            elif assignment_name == 'Assignment 4':
                row['milestone1'] = 1461020400000
                row['milestone2'] = 1461366000000
                row['milestone3'] = 1461884400000
                row['earlyBonus'] = 1462402800000
                row['dueTime'] = 1462417200000
            else:
                row['milestone1'] = -1
                row['milestone2'] = -1
                row['milestone3'] = -1
                row['earlyBonus'] = -1
                row['dueTime'] = -1


            # Stores launchtypes and terminationtypes less nonsensically.
            if repr(row['Type']) == repr('Launch'):
                row['Subtype'] = row['LaunchType']
            elif repr(row['Type']) == repr('Termination'):
                row['Subtype'] = row['TerminationType']

            del row['LaunchType']
            del row['TerminationType']

            writer.writerow(row)

def squashed_assignment_name(assignment):
    split = assignment.split()
    return split[0] + ' ' + split[1]

def project_dir_from_uri(uri):
    split = uri.split('/')
    assignment_keywords = [ 'assignment', 'project', 'rectangle', 'point' ]
    for thing in split:
        thing = thing.replace('%20', '').lower()
        if any(keyword in thing for keyword in assignment_keywords):
            nums = re.findall(r'\d+', thing)
            for num in nums:
                if num in ['1', '2', '3', '4']:
                    return 'Assignment ' + num
    return None

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        clean_assignment_names(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File %s does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:\n\t./clean.py <input_file> <output_file>')
        sys.exit()
    main(sys.argv[1:])
