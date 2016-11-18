#! /usr/bin/env python3

# In[]:
import sys
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale

if (len(sys.argv) < 4):
    print_usage()
    sys.exit()

if (sys.argv[1] not in ['kmeans']):
    print_usage()
    sys.exit()

method = sys.argv[1]
infile = sys.argv[2]
outfile = sys.argv[3]

# In[]:
def kmeans(data, outfile):
    scaled = scale(data, copy=True)
    clusters = KMeans(n_clusters=4, random_state=10).fit_predict(scaled)
    data['cluster'] = clusters
    data.head()

    # In[]: Write out
    data.to_csv(outfile)

def get_data(infile, index_col=None):
    data = pd.read_csv(infile, index_col=index_col)
    data = data.dropna(how='any').drop(['submissionCount', 'email'], 1)
    data.head()
    return data

def print_usage():
    print('Performs clustering based on raw incremental development metrics.')
    print('Usage:\n\t./cluster.py <cluster method> <input file> <output file>')

def main(args):
    method = args[0].lower()
    infile = args[1]
    outfile = args[2]
    try:
        if (method == 'kmeans'):
            kmeans(infile, outfile)
        else:
            print_usage()
    except FileNotFoundError as e:
        print('File not found. Please check that "%s" exists.' % infile)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print_usage()
    main(sys.argv[1:])
