#! /usr/bin/env python3

import csv
import sys

def print_headers(infile):
    """Prints all the headers in the infile"""
    print('Prints CSV headers in %s data:' % infile)
    headers = None

    with open(infile, 'r') as fin:
        reader = csv.reader(fin, delimiter=',')
        headers = next(reader)

    for thing in headers:
        print(thing)

def print_distinct(infile, fieldname):
    """
    Prints all distinct values found in given column.

    Keyword arguments:
    infile    -- the input data file (CSV)
    fieldname -- the name of the column.
    """
    print("Printing all distinct values from column %s." % fieldname)
    values = []
    try:
        with open(infile, 'r') as fin:
            for row in csv.DictReader(fin, delimiter=','):
                if (repr(row[fieldname]) not in values):
                    values.append(repr(row[fieldname]))
    except FileNotFoundError as fnfe:
        print("Error! %s does not exist!" % infile)
    except KeyError as ke:
        print("Error! There is no column '%s' in the csv file %s." % (fieldname, infile))


    for thing in values:
        print(thing)


def get_sample(infile, col_index, vals, outfile):
    """
    Gets all raw sensordata for the project_ids in the specified list.

    Keyword arguments:
    outfile -- the file in which to put the sample.
    """
    print("Sampling by given column values and putting them in %s..." % (outfile))

    try:
        with open(infile, 'r') as fin, open(outfile, 'w') as fout:
            writer = csv.writer(fout, delimiter=',')
            reader = csv.reader(fin, delimiter=',')
            headers = next(reader)
            writer.writerow(headers)
            for row in csv.reader(fin, delimiter=','):
                if (repr(row[col_index]) in vals):
                    writer.writerow(row)
    except FileNotFoundError as fnfe:
        print("Error! %s does not exist!" % infile)

def main(args):
    if args[0] in 'sample':
        if len(args) < 4:
            print_usage()
            sys.exit()
        infile = args[1]
        col_index = args[2]
        vals = [repr(x) for x in args[3:len(args) - 1]]
        outfile = args[len(args) - 1]
        get_sample(infile, int(col_index), vals, outfile)
    elif args[0] in 'dist':
        if len(args) < 3:
            print_usage()
            sys.exit()
        infile = args[1]
        fieldname = args[2]
        print_distinct(infile, fieldname)
    elif args[0] in 'headers':
        if len(args) < 2:
            print_usage()
            sys.exit()
        infile = args[1]
        print_headers(infile)
    else:
        print_usage()

def print_usage():
    print("Get a sample from, all the headers in, or all distinct values for a field - from the " + 
        "given data file.")
    print("Usage: ./misc.py sample [input_file] [col_index] [vals,] [output_file]")
    print("OR: ./misc.py dist [input_file] [fieldname]")
    print("OR: ./misc.py headers [input_file]")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit()
    main(sys.argv[1:])
