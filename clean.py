#! /usr/bin/env python3

import csv
import sys

def clean_assignment_names(infile, outfile):
    """
    Makes an attempt to clean sensordata. Marks lines that we are not sure of.
    Focuses on making sure assignment names are properly assigned to student
    events.

    Keyword arguments:
    infile  -- the file containing the unclean sensordata
    outfile -- the file containing the clean sensordata, with an added column 'clean?'
        to indicate whether the event has been cleaned or not.
    """
    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        headers = list((fn) for fn in reader.fieldnames)
        headers.append('clean?')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=headers)

        # Write headers first
        writer.writerow(dict((fn, fn) for fn in writer.fieldnames))

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        clean_assignment_names(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File %s does not exist." % infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:\n\t./subsessions.py [input_file] [output_file]')
        sys.exit()
    main(sys.argv[1:])
