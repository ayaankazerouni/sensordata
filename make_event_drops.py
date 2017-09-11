#! /usr/bin/env python3

# In[]: import lib and data
import pandas as pd
from datetime import datetime

infile = '~/Desktop/p1-10116.csv'
dtypes = {
    'userId': str,
    'projectId': str,
    'email': str,
    'CASSIGNMENTNAME': str,
    'time': int,
    'Type': object,
    'Subtype': object,
    'onTestCase': object
}
df = pd.read_csv(infile, \
        dtype=dtypes, \
        na_values=[], \
        low_memory=False, \
        usecols=list(dtypes.keys()), \
        index_col=False)
df.sort_values(by='time', ascending=[1], inplace=True)
df.fillna('', inplace=True)
df = df[df['Type'].isin(['Edit', 'Launch'])]
df.loc[(df.Type == 'Edit') & (df.onTestCase == '1'), 'Subtype'] = 'Test'
df.loc[(df.Type == 'Edit') & (df.onTestCase == '0'), 'Subtype'] = 'Normal'

# In[]: df is only Edits and Launches
type_groups = df.groupby(['Type', 'Subtype'], as_index=False)
