#! /usr/bin/env python3

# Toy script for putting data in the format required by https://github.com/marmelab/EventDrops

# In[]: import lib and data
import pandas as pd
import numpy as np

infile = '~/Desktop/p1-10116.csv' # sample file for testing
outfile = 'visualisations/results/p1-10116-eventDrops.json'
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
type_groups = df.groupby(['Type', 'Subtype'])
type_groups = type_groups.aggregate({ 'time': lambda t: tuple(t) }).reset_index()
type_groups['Type'] += type_groups['Subtype']
type_groups.rename(columns={ 'Type': 'name', 'time': 'data' }, inplace=True) # event-drops expects this
type_groups = type_groups.drop('Subtype', axis=1)


# In[]: write out json
type_groups.to_json(path_or_buf=outfile, orient='records')
