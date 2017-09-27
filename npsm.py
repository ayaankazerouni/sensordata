# See Carter et al. http://dl.acm.org/citation.cfm?doid=2787622.2787710

import pandas as pd
from datetime import datetime

# States
EDITING_NORMAL = 'Yn'
EDITING_TEST = 'Yt'
EXECUTING_NORMAL = 'En'
EXECUTING_TEST = 'Et'
UNKNOWN = 'N'

infile = 'data/fall-2016/p1-sample.csv'
dtypes = {
    'userId': str,
    'projectId': str,
    'CASSIGNMENTNAME': str,
    'time': int,
    'Class-Name': object,
    'Unit-Type': object,
    'Type': object,
    'Subtype': object,
    'Subsubtype': object,
    'onTestCase': object,
    'Current-Statements': object,
    'Current-Methods': object,
    'Current-Size': object,
    'Current-Test-Assertions': object
}
df = pd.read_csv(infile, dtype=dtypes, na_values=[], low_memory=False, usecols=list(dtypes.keys()))
df.sort_values(by=['time'], ascending=[1], inplace=True)
df.fillna('', inplace=True)

# right now data is only from one user
# userdata = df.groupby(['userId'])
# results = userdata.apply(usernpsm)

df = df[df.Type.isin(['Edit', 'Launch'])]
df.loc[(df.Type == 'Edit') & (df.onTestCase == '1'), 'State'] = EDITING_TEST
df.loc[(df.Type == 'Edit') & (df.onTestCase == '0'), 'State'] = EDITING_NORMAL
df.loc[(df.Type == 'Launch') & (df.Subtype == 'Test'), 'State'] = EXECUTING_TEST
df.loc[(df.Type == 'Launch') & (df.Subtype == 'Normal'), 'State'] = EXECUTING_NORMAL


prev_row = None
current_state_start_time = None

for index, row in df.iterrows():
    time = datetime.fromtimestamp(int(float(row.time)) / 1000)
    if prev_row is not None:
        prev_time = datetime.fromtimestamp(int(float(prev_row.time)) / 1000)
        diffmin = (time - prev_time).total_seconds() / 60
        prev_state = prev_row.State
    else:
        diffmin = 0
        prev_state = UNKNOWN

    if diffmin <= 3:
        if prev_state != row.State:
            transition = prev_state + row.State
        else:
            transition = row.State
