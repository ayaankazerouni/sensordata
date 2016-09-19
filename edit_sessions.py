#! /usr/bin/env python3

import csv
import sys

def get_edit_sessions(infile, outfile):
    fieldnames = [
        'projectId',
        'userId',
        'cleaned_assignment',
        'size',
        'editType'
    ]

    with open(infile, 'r') as fin, open(outfile, 'w') as fout:
        reader = csv.DictReader(fin, delimiter=',')
        writer = csv.DictWriter(fout, delimiter=',', fieldnames=fieldnames)

        # Write headers first.
        writer.writerow(dict((fn, fn) for fn in fieldnames))

        prev_row = None
        running_edit_total = 0
        prev_edit_type = None
        curr_sizes = {}

        for row in reader:
            prev_row = prev_row or row

            if (row['userId'] == prev_row['userId'] and row['projectId'] == prev_row['projectId']):
                if (repr(row['Type']) == repr('Edit')):
                    if (len(row['Class-Name']) > 0):
                        edit_type = get_edit_type(int(row['onTestCase']))
                        prev_edit_type = prev_edit_type or edit_type

                        if (prev_edit_type != edit_type):
                            to_write = {
                                'projectId': prev_row['projectId'],
                                'userId': prev_row['userId'],
                                'cleaned_assignment': prev_row['cleaned_assignment'],
                                'size': running_edit_total,
                                'editType': prev_edit_type
                            }

                            writer.writerow(to_write)

                            running_edit_total = 0

                        class_name = repr(row['Class-Name'])
                        stmts = int(row['Current-Statements'])
                        prev_size = curr_sizes.get(class_name, 0)
                        curr_sizes[class_name] = stmts

                        running_edit_total += abs(stmts - prev_size)

                        prev_edit_type = edit_type
                prev_row = row
            else:
                to_write = {
                    'projectId': prev_row['projectId'],
                    'userId': prev_row['userId'],
                    'cleaned_assignment': prev_row['cleaned_assignment'],
                    'size': running_edit_total,
                    'editType': prev_edit_type
                }

                writer.writerow(to_write)

                curr_sizes = {}

                if (repr(row['Type']) == repr('Edit')):
                    if (len(row['Class-Name']) > 0):
                        edit_type = get_edit_type(int(row['onTestCase']))

                        class_name = repr(row['Class-Name'])
                        stmts = int(row['Current-Statements'])
                        prev_size = curr_sizes.get(class_name, 0)
                        curr_sizes[class_name] = stmts

                        running_edit_total = abs(stmts - prev_size)

                        prev_edit_type = edit_type

                prev_row = row

        to_write = {
            'projectId': prev_row['projectId'],
            'userId': prev_row['userId'],
            'cleaned_assignment': prev_row['cleaned_assignment'],
            'size': running_edit_total,
            'editType': prev_edit_type
        }

        writer.writerow(to_write)

def get_edit_type(edit_type):
    if edit_type == 1:
        return 'Test'
    elif edit_type == 0:
        return 'Normal'
    else:
        return None

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        get_edit_sessions(infile, outfile)
    except FileNotFoundError as e:
        print("Error! File '%s' does not exist." % infile)
    except KeyError as e:
        cause = e.args[0]
        if (cause == 'cleaned_assignment'):
            print("Key Error! Are you using a cleaned data file? Please run ./clean.py on the data file and use " +
                "the resulting file as input.")
        else:
            traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Squashes data into alternating edit sessions and test edit sessions.')
        print('Usage:\n\t./edit_sessions.py <input_file> <output_file>')
        sys.exit()
    main(sys.argv[1:])
