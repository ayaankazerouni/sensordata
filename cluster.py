#! /usr/bin/env python3

# In[]:
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA

def print_usage():
    print('Performs clustering based on raw incremental development metrics.')
    print('Usage:\n\t./cluster.py <cluster method> <input file> <output file>')

def kmeans(data, n_clusters, outfile=None):
    scaled = scale(data, copy=True)
    clusters = KMeans(n_clusters=n_clusters, random_state=10).fit_predict(scaled)
    data['cluster'] = clusters

    described = data.groupby('cluster').apply(lambda x: x.mean())
    described.drop('cluster', axis=1, inplace=True)
    data.drop('cluster', axis=1, inplace=True)

    if (outfile is not None):
        described.to_csv(outfile)

    return clusters

def do_pca(data):
    pca = PCA(n_components=2)
    existing_2d = pca.fit_transform(data)
    existing_df_2d = pd.DataFrame(existing_2d)
    existing_df_2d.columns = ['PC1', 'PC2']

    return existing_df_2d

# In[]:
infile = 'data/fall-2016/incremental_checking.xlsx'
method = 'kmeans'
outfile = None
n_clusters = 3

# read command line arugments if this is NOT being run in an IPython context
if ('ipykernel' not in sys.argv[0]):
    if (len(sys.argv) < 4 or sys.argv[1] not in ['kmeans']):
        print_usage()
        sys.exit()
    else:
        method = sys.argv[1]
        infile = sys.argv[2]
        outfile = sys.argv[3]
        if (len(sys.argv) < 5):
            n_clusters = 3
        else:
            n_clusters = int(sys.arv[4])
# In[]:
data = pd.read_excel(infile, header=5, parse_cols='A,B,C,E,G,I,K,M,O')
data.set_index(['userId', 'Assignment'], inplace=True)
data.drop(['email', 'Total Grade'], inplace=True, axis=1)
data.head()

# In[]:
existing_df_2d = do_pca(data)

if (method == 'kmeans'):
    clusters = kmeans(data, n_clusters=n_clusters, outfile=outfile)

existing_df_2d['cluster'] = pd.Series(clusters, index=existing_df_2d.index)
existing_df_2d.plot(kind='scatter', x='PC2', y='PC1', c=existing_df_2d.cluster.astype(np.float), figsize=(16,8))
plt.show()
