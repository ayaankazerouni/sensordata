#! /usr/bin/env python3

# In[]:
import sys
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale

# In[]:
def print_usage():
    print('Performs clustering based on raw incremental development metrics.')
    print('Usage:\n\t./cluster.py <cluster method> <input file> <output file>')

def kmeans(data, outfile=None):
    scaled = scale(data, copy=True)
    clusters = KMeans(n_clusters=4, random_state=10).fit_predict(scaled)
    data['cluster'] = clusters
    data.head()

    described = data.groupby('cluster').apply(lambda x: x.describe())
    described.drop('cluster', axis=1, inplace=True)

    if (outfile is not None):
        described.to_csv(outfile)

    return described

# In[]:
infile = 'data/fall-2016/incremental_checking.xlsx'
method = 'kmeans'
outfile = None

if ('ipykernel' not in sys.argv[0]):
    if (len(sys.argv) < 4 or sys.argv[1] not in ['kmeans']):
        print_usage()
        sys.exit()
    else:
        method = sys.argv[1]
        infile = sys.argv[2]
        outfile = sys.argv[3]

# In[]:
data = pd.read_excel(infile, header=5, parse_cols='A,B,C,E,G,I,K,M,O')
data.set_index(['Assignment', 'userId'], inplace=True)
data.drop('email', inplace=True, axis=1)
data.head()

# In[]:
if (method == 'kmeans'):
    clusters = kmeans(data, outfile)

clusters
