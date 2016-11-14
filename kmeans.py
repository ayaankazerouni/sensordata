# In[]:
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale

data = pd.read_csv('data/fall-2016/incremental_checking.csv', index_col=['CASSIGNMENTNAME', 'userId']).dropna(how='any').drop(['submissionCount', 'email'], 1)
scale(data, axis=1, copy=False)
data.head()

# In[]:
clusters = KMeans(n_clusters=4, random_state=10).fit_predict(data)
data['cluster'] = clusters
data.head()
