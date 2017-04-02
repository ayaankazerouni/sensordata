#! /usr/bin/env python3

import csv
import sys

def print_headers(infile):
    """Prints all the headers in infile"""
    print('Printing CSV headers in %s data:' % infile)
    headers = None

    with open(infile, 'r') as fin:
        reader = csv.reader(fin, delimiter=',')
        headers = next(reader)

    for thing in headers:
        print(thing)

def print_distinct(infile, fieldname, limit=None):
    """
    Prints all distinct values found in given column.

    Keyword arguments:
    infile    -- the input data file (CSV)
    fieldname -- the name of the column.
    """
    limstr = "all" if limit is None else str(limit)
    print("Printing %s distinct values from column '%s'." % (limstr, fieldname))
    limit = limit or sys.maxsize
    values = []
    try:
        with open(infile, 'r') as fin:
            for row in csv.DictReader(fin, delimiter=','):
                if len(values) < limit and repr(row[fieldname]) not in values:
                    values.append(repr(row[fieldname]))
                elif len(values) >= limit:
                    break

    except FileNotFoundError as fnfe:
        print("Error! %s does not exist!" % infile)
    except KeyError as ke:
        print("Error! There is no column '%s' in the csv file %s." % (fieldname, infile))


    for thing in values:
        print(thing)


def get_sample(infile, col, vals, outfile):
    """
    Gets all raw sensordata for the project_ids in the specified list.

    Keyword arguments:
    outfile -- the file in which to put the sample.
    """
    print("Sampling by %s into %s..." % (col, outfile))

    try:
        with open(infile, 'r') as fin, open(outfile, 'w') as fout:
            reader = csv.DictReader(fin, delimiter=',')
            writer = csv.DictWriter(fout, delimiter=',', fieldnames=reader.fieldnames)
            # Write headers first.
            writer.writerow(dict((fn, fn) for fn in writer.fieldnames))
            for row in reader:
                if (repr(row[col]) in vals):
                    writer.writerow(row)
    except FileNotFoundError as fnfe:
        print("Error! %s does not exist!" % infile)

def main(args):
    if args[0] in 'sample':
        if len(args) < 4:
            print_usage()
            sys.exit()
        infile = args[1]
        col = args[2]
        vals = [repr(x) for x in args[3:len(args) - 1]]
        outfile = args[len(args) - 1]
        get_sample(infile, col, vals, outfile)
    elif args[0] in ['dist', 'distinct']:
        if len(args) < 3:
            print_usage()
            sys.exit()
        infile = args[1]
        fieldname = args[2]
        if len(args) == 4:
            print_distinct(infile, fieldname, int(args[3]))
        else:
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
    print("Get a sample, all the headers, or all distinct values for a field - from the " +
        "given data file.")
    print("Usage: ./misc.py sample <input_file> <column_name> <vals,> <output_file>")
    print("OR: ./misc.py dist|distinct <input_file> <fieldname> [limit]")
    print("OR: ./misc.py headers <input_file>")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit()
    main(sys.argv[1:])
