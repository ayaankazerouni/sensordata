from collections import Counter
import pandas as pd

infile = 'data/p1-10116.csv'
dtypes = {
    'time': int,
    'Type': object,
    'Subtype': object,
    'onTestCase': object
}
df = pd.read_csv(infile, dtype=dtypes, na_values=[], low_memory=False, usecols=list(dtypes.keys()))
df.sort_values(by=['time'], ascending=[1], inplace=True)
df.fillna('', inplace=True)

df = df[(df['Type'].isin(['Edit', 'Launch']))]
df.loc[(df.Type == 'Edit') & (df.onTestCase == '1'), 'Subtype'] = 'Test'
df.loc[(df.Type == 'Edit') & (df.onTestCase == '0'), 'Subtype'] = 'Normal'
df.str = df['Type'] + df['Subtype']
df.str = df.str.apply(getstr)
vals = df.str.values.tolist()
vals = ''.join(vals)

counts = Counter(vals[i:i+6] for i in range(len(vals) - 5))
counts.most_common(20)


def getstr(val):
    if val == 'EditTest':
        return 'T'
    elif val == 'EditNormal':
        return 'N'
    elif val == 'LaunchNormal':
        return 'L'
    else:
        return 'U'
