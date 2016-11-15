"""
Grade prediction from incremental development metrics.
"""
# In[]: Preparing the data: Importing
import pandas as pd

webcat = pd.read_csv('data/fall-2016/web-cat-students-with-sensordata.csv')
webcat.rename(columns={'assignment': 'CASSIGNMENTNAME', 'userName': 'email'}, inplace=True)
webcat['email'] = webcat['email'] + '@vt.edu'
webcat.sort_values(by=['CASSIGNMENTNAME', 'email', 'submissionNo'], ascending=[1,1,0], inplace=True)
webcat.head()

# In[]: Preparing the data: Getting the maximum grade achieved by each student on each project
def maxscore(submission):
    first = submission.iloc[0]
    max_score = first['MCS.score.correctness']
    max_possible = first['max.score.correctness']
    percent = (max_score / max_possible) * 100
    if (percent > 90):
        return 1
    elif (percent > 80):
        return 2
    elif (percent > 70):
        return 3
    else:
        return 4

scores = webcat.groupby(['CASSIGNMENTNAME', 'email']).apply(maxscore)
scores

# In[]: Preparing the data: Getting incremental development results
inc = pd.read_csv('data/fall-2016/incremental_checking.csv')
