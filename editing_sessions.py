import csv
import sys

def get_editing_index(infile, outfile):
    fieldnames = [
        'projectId',
        'userId',
        'cleaned_assignment',
        'editToTestTotal'
    ]

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in fieldnames))

        prev_row = None
        running_edit_total = 0
        running_test_edit_total = 0
        prev_edit_type = None
        curr_sizes = {}

        for row in reader:
            prev_row = prev_row or row

            if (row['userId'] == prev_row['projectId'] and row['projectId'] == prev_row['projectId']):
                if (repr(row['Type']) == repr('Edit')):
                    if (len(row['Class-Name']) > 0):
                        class_name = repr(row['Class-Name'])
                        stmts = int(row['Current-Statements'])
                        prev_size = curr_sizes.get(class_name, 0)
