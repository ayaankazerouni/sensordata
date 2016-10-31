#! /usr/bin/env python3

import csv
import sys
import re

def clean_assignment_names(infile, outfile, clean_launches=None):
    """
    * Assigns cleaned assignment names to each row, making an educated guess
      by looking at the URI for that sensordata event.
    * Stores Launch and Termination information in the Type and Subtype columns.

    Keyword arguments:
    infile  -- the file containing the unclean sensordata
    outfile -- the file containing the clean sensordata, with an added
        column 'cleaned_assignment'. This column is used for other aggregation
        operations (subsessions, work_sessions, etc.).
    clean_launches -- true (or any non-None) value to indicate whether launches need to be
        cleaned up or not.
    """
    print("This could take a few minutes, depending on how large the input is.")
    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        headers = list((fn) for fn in reader.fieldnames)
        headers.append('cleaned_assignment')
        headers.append('cleaned?')
        if (clean_launches != None):
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
            project_dir = assignment_name_from_uri(uri)

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

            # Stores launchtypes and terminationtypes less nonsensically.
            if (clean_launches != None):
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

def assignment_name_from_uri(uri):
    split = uri.split('/')
    assignment_keywords = [ 'assignment', 'project', 'program' ]
    for thing in split:
        thing = thing.replace('%20', '').replace('_', '').lower()
        regexp = re.compile(r'[p|P][1|2]')
        if any(keyword in thing for keyword in assignment_keywords) or regexp.search(thing) is not None:
            nums = re.findall(r'\d+', thing)
            for num in nums:
                if num in ['1', '2']:
                    return 'Project ' + num


    return None

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        if (len(args) == 3):
            clean_launches = args[2]
            clean_assignment_names(infile, outfile, clean_launches)
        else:
            clean_assignment_names(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File %s does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:\n\t./clean.py <input_file> <output_file> [clean_launches]')
        sys.exit()
    main(sys.argv[1:])
