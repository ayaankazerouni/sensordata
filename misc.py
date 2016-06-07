#! /usr/bin/env python3

import csv

def get_sample(project_ids, outfile):
    """
    Gets all raw sensordata for the project_ids in the specified list.

    Keyword arguments:
    outfile -- the file in which to put the sample.
    """
    print("Sampling by projectIds given and putting them in %s..." % (outfile))
    with open('../sensordata.csv', 'r') as fin, open(outfile, 'w') as fout:
        writer = csv.writer(fout, delimiter=',')
        reader = csv.reader(fin, delimiter=',')
        headers = next(reader)
        writer.writerow(headers)
        for row in csv.reader(fin, delimiter=','):
            if (repr(row[0]) in project_ids):
                writer.writerow(row)

def print_distinct(infile, fieldname):
    """
    Prints all distinct values found in given column.

    Keyword arguments:
    infile    -- the input data file (CSV)
    fieldname -- the name of the column.
    """
    values = []
    with open(infile, 'r') as fin:
        for row in csv.DictReader(fin, delimiter=','):
            if (repr(row[fieldname]) not in values):
                values.append(repr(row[fieldname]))

    for thing in values:
        print(thing)
