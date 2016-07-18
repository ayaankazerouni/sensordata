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
        headers.append('cleaned_assignment')
        headers.append('cleaned?')

        writer = csv.DictWriter(fout, delimiter=',', fieldnames=headers)
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
                row['cleaned_assignment'] = project_dir
                row['cleaned?'] = 1
            else:
                row['cleaned_assignment'] = assignment_name
                row['cleaned?'] = 1

            writer.writerow(row)

def squashed_assignment_name(assignment):
    split = assignment.split()
    return split[0] + split[1]

def project_dir_from_uri(uri):
    split = uri.split('/')
    for thing in split:
        if thing.startswith('Assignment') or thing.startswith('Project')\
            or thing.startswith('Rectangle') or thing.startswith('Point')\
            or thing.startswith('project'):
                thing = thing.replace('%20', '')
                nums = re.findall(r'\d+', thing)
                for num in nums:
                    if num in ['1', '2', '3', '4']:
                        return 'Assignment' + num
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
