
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import math
import datetime

df = pd.read_csv('data/fall-2016/web-cat-students-with-sensordata.csv')
df.sort_values(by=['assignment', 'userName', 'submissionNo'], ascending=[1,1,0], inplace=True)
df.head(2)


# In[4]:

# group data by unique values of ('assignment', 'userName'). So all the data
# for a student's submisisons to one assignment will be together
assignments = df.groupby(['assignment', 'userName'])

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
            daystofinallist.append((finalsubmissiontime - submissiontime).days)

            # we are looping through the submissions in reverse order,
            # so calculations for gain will also be reversed.
            testpercent = int(row['score.correctness']) / int(row['max.score.correctness'])
            elpercent = int(row['elementsCovered']) / int(row['elements'])
            refpercent = testpercent / elpercent
            delta = prevpercent - refpercent if prevpercent is not None else refpercent

            if (delta < 0):
                dropcount += 1
            elif (delta > 0):
                gaincount += 1
                weightedgainpercent += (gaincount / submissioncount) * daystofinal
            else:
                flatcount += 1
            prevpercent = refpercent

    median = np.percentile(daystofinallist, 50)
    earlyoften = weightedgainpercent / gaincount if gaincount > 0 else float('nan')
    results = {
        'submissionCount': submissioncount,
        'dropPercent': (dropcount / submissioncount) * 100,
        'flatPercent': (flatcount / submissioncount) * 100,
        'gainPercent': (gaincount / submissioncount) * 100,
        'medianDaysToFinal': median,
        'refGainEarlyOften': earlyoften
    }
    return pd.Series(results)

results = assignments.apply(userdata)
results


# In[5]:

results.describe()


# In[7]:

results.to_csv('data/fall-2016/webcat-results.csv')
