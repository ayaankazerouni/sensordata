#! /usr/bin/env python3

# In[]:
import sys
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale

# In[]:
def kmeans(infile, outfile):
    # In[]: Uncomment the following line and hard-code infile and run this as
    # as a standalone cell
    # infile =
    data = get_data(infile, index_col=['CASSIGNMENTNAME', 'userId'])
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
    sys.exit()

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
