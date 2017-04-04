#! /usr/bin/env python3

# In[]:
import sys
import pandas as pd
import numpy as np
import math
import datetime

def userdata(usergroup):
    """
    This function acts on data for one student's submission to one
    assignment. The data resides in the specified argument.

    Keyword arguments:
    usergroup -- pandas.DataFrame
    """
    prevpercent = None
    dropcount = 0
    gaincount = 0
    flatcount = 0
    noncompiling = 0
    submissioncount = 0
    daystofinal = 0
    daystofinallist = []
    weightedgainpercent = 0

    finalsubmissiontime = datetime.date.fromtimestamp(usergroup.iloc[0]['submissionTimeRaw'] / 1000)

    for index, row in usergroup.iterrows():
        submissioncount += 1
        if (not math.isnan(row['score.correctness']) and abs(int(row['elements'])) > 0):
            submissiontime = datetime.date.fromtimestamp(int(row['submissionTimeRaw']) / 1000)
            daystofinal = (finalsubmissiontime - submissiontime).days
            daystofinallist.append(daystofinal)

            # we are looping through the submissions in reverse order,
            # so calculations for gain will also be reversed.
            testpercent = int(row['score.correctness']) / int(row['max.score.correctness'])
            elpercent = int(row['elementsCovered']) / int(row['elements'])
            refpercent = testpercent / elpercent if elpercent != 0 else testpercent
            delta = prevpercent - refpercent if prevpercent is not None else refpercent

            if (delta < 0):
                dropcount += 1
            elif (delta > 0):
                gaincount += 1
                weightedgainpercent += (gaincount / submissioncount)
            else:
                flatcount += 1
            prevpercent = refpercent

    median = np.nanpercentile(daystofinallist, 50)
    earlyoften = weightedgainpercent / gaincount if gaincount > 0 else float('nan')
    results = {
        'submissionCount': submissioncount,
        'dropCount': dropcount,
        'flatCount': flatcount,
        'gainCount': gaincount,
        'medianDaysToFinal': median,
        'refGainEarlyOften': earlyoften
    }
    return pd.Series(results)

def pos(n):
    """
    Returns this number's position on the number line in relation to 0.
    """
    if n > 0:
        return 1
    elif n < 0:
        return -1
    else:
        return 0

def reference_test_gains(infile, outfile):
    # In[]: Import data
    df = pd.read_csv(infile)
    df.sort_values(by=['assignment', 'userName', 'submissionNo'], ascending=[1,1,0], inplace=True)
    df.head(2)

    # In[]: Group data by unique values of ('assignment', 'userName'). So all the data
    # for a student's submissions to one assignment will be together
    assignments = df.groupby(['assignment', 'userName'])

    results = assignments.apply(userdata)
    results

    # In[]: Write out
    results.to_csv(outfile)

def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        reference_test_gains(infile, outfile)
    except FileNotFoundError as e:
        print('File not found. Please check that "%s" exists.' % infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Calculates Web-CAT reference test gain measures from the given student submission data.')
        print('Usage:\n\t./reference_test_gains <input file> <output file>')
        sys.exit()
    main(sys.argv[1:])
