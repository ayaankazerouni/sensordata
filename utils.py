"""Convenience methods for common tasks, such as retrieiving
subsets of events, converting timestamps, getting a term, etc.

To use:
    `import utils`
"""
import re
import csv
import copy
import logging
import datetime
from urllib import parse

import numpy as np
import pandas as pd

logging.basicConfig(filename='sensordata-utils.log', filemode='w', level=logging.WARN)

def load_launches(launch_path=None, sensordata_path=None, newformat=True):
    """Loads raw launch data.

    Convenience method: filters out everything but Launches from raw sensordata,
    or reads launches from an already filtered CSV file. If both are specified,
    the launch_path will be given precedence.

    Newformat info: The new format encodes test success info differently; the old format
    included columns 'TestSucesses' (notice the typo) and 'TestFailures'; the new format
    instead include the column 'Unit-Name'. The new format also includes ConsoleOutput,
    which was not present earlier. Use the default True for data collected after Fall 2018,
    False for earlier.

    Args:
        launch_path (str): Path to file containing already filtered launch data
        sensordata_path (str): Path to file containing raw sensordata
        newformat (bool, default=True): Use the new format?
    """
    errormessage = "Either launch_path or sensordata_path must be specified and non-empty."
    if not launch_path and not sensordata_path:
        raise ValueError(errormessage)

    if launch_path:
        try:
            launches = pd.read_csv(launch_path) # no need to do any formatting, either
            return launches
        except FileNotFoundError:
            if not sensordata_path:
                raise ValueError(errormessage)

    dtypes = {
        'email': str,
        'CASSIGNMENTNAME': str,
        'time': float,
        'Type': str,
        'Subtype': str,
        'Subsubtype': str,
    }
    if newformat:
        dtypes['Unit-Name'] = str
        dtypes['ConsoleOutput'] = str
    else:
        dtypes['TestSucesses'] = str
        dtypes['TestFailures'] = str

    # pylint: disable=unused-variable
    eventtypes = ['Launch', 'Termination']
    data = pd.read_csv(sensordata_path, dtype=dtypes, usecols=dtypes.keys()) \
             .query('Type in @eventtypes') \
             .rename(columns={
                 'email': 'userName',
                 'CASSIGNMENTNAME': 'assignment'
             })
    data.userName = data.userName.apply(lambda u: u.split('@')[0])
    data = data.set_index(['userName', 'assignment'])
    return data

def get_term(timestamp):
    """Returns a term id based on a timestamp in seconds. If the provided
    timestamp is in milliseconds this method will truncate the timestamp to seconds.
    """
    inmillis = len(str(abs(timestamp))) >= 13
    if inmillis:
        timestamp = int(timestamp / 1000)
    eventtime = datetime.datetime.fromtimestamp(timestamp)
    year = eventtime.year
    month = eventtime.month

    if month >= 8:
        return 'fall%d' % year

    if month >= 7: # TODO: Deal with summer terms?
        return 'summer-1-%d' % year

    if month > 5:
        return 'summer-2-%d' % year

    if month >= 1:
        return 'spring%d' % year

    return None

def load_edits(edit_path=None, sensordata_path=None, assignment_col='assignment'):
    """Loads edit events that took place on a source file.

    This convenience method filters out Edit events from raw sensordata, or
    reads an already filtered CSV file. If both edit_path and sensordata_path
    are specified, the already-filtered file (at edit_path) takes precedence.
    """
    if not edit_path and not sensordata_path:
        raise ValueError("Either edit_path or sensordata_path must be specified and non-empty")

    if edit_path:
        try:
            edits = pd.read_csv(edit_path) # no formatting needed
            return edits
        except FileNotFoundError:
            if not sensordata_path:
                raise ValueError("edit_path is invalid and sensordata_path not specified.")

    # edit_path was invalid, so we need to get edit events from all sensordata
    dtypes = {
        'email': str,
        assignment_col: str,
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
    data = pd.read_csv(sensordata_path, dtype=dtypes, usecols=dtypes.keys())
    data = data[(data['Type'] == 'Edit') & (data['Class-Name'] != '')]
    data = data.fillna('') \
               .sort_values(by=['email', assignment_col, 'time'], ascending=[1, 1, 1]) \
               .rename(columns={'email': 'userName', assignment_col: 'assignment'})
    data['userName'] = data.userName.apply(lambda u: u.split('@')[0])
    data = data.set_index(['userName', 'assignment'])
    return data

#: The typical fieldnames included in sensordata events. 
DEFAULT_FIELDNAMES = [
    'email',
    'CASSIGNMENTNAME',
    'time',
    'Class-Name',
    'Unit-Type',
    'Unit-Name',
    'From-Unit-Name',
    'To-Unit-Name',
    'Type',
    'Subtype',
    'Subsubtype',
    'onTestCase',
    'Current-Statements',
    'Current-Methods',
    'Current-Size',
    'Current-Test-Assertions',
    'ConsoleOutput'
]

def raw_to_csv(inpath, outpath, fieldnames=None):
    """
    Given a file of newline separated URLs, writes the URL query params as
    rows in CSV format to the specified output file.

    If your URLs are DevEventTracker posted events, then you probably want
    the :attr:`DEFAULT_FIELDNAMES`. These fieldnames can be imported  and 
    modified as needed.
    """
    with open(inpath, 'r') as infile, open(outpath, 'w') as outfile:
        if not fieldnames:
            fieldnames = DEFAULT_FIELDNAMES
        writer = csv.DictWriter(outfile, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()

        for line in infile:
            event = processline(line, fieldnames)
            if event is not None:
                if isinstance(event, list):
                    for item in event:
                        writer.writerow(item)
                else:
                    writer.writerow(event)

def processline(url, fieldnames=None, filtertype=None):
    """
    Given a URL, returns a dict object containing the key-value
    pairs from its query params. Filters for a specific Type if specified.

    Args: 
        fieldnames (list, default=None): The list of fieldnames to capture. If `None`,
                                         uses `DEFAULT_FIELDNAMES`.
        filtertype (bool): Only return a dict if the query param for Type == filtertype

    Returns:
        (dict) containing the key-value pairs from the the url's query params.
    """
    if not fieldnames:
        fieldnames = DEFAULT_FIELDNAMES
    if 'http' in url:
        url = url.split(':', 1)[-1]
    items = parse.parse_qs(parse.urlparse(url).query)
    kvpairs = {}
    for key, value in items.items():
        if _shouldwritekey(key, fieldnames):
            kvpairs[key] = value[0].rstrip('\n\r')
        elif key.startswith('name'): # some items are in the form name0=somekey, value0=somevalue
            k = value[0] # e.g., "name0=k"
            num = re.search(r'(\d+)$', key).group(0)
            val = items.get('value{}'.format(num), [''])[0] # e.g., "value0=v", "value0="
            if _shouldwritekey(k, fieldnames):
                kvpairs[k] = val.rstrip('\n\r')
    time = int(float(kvpairs.get('time', 0))) # time is not guaranteed to be present
    kvpairs['time'] = time if time != 0 else ''
    if filtertype and kvpairs['Type'] != filtertype:
        return None

    if kvpairs.get('Class-Name', '').endswith('Test') and \
        kvpairs.get('Current-Test-Assertions', 0) != 0:
        kvpairs['onTestCase'] = 1

    return kvpairs


def split_termination_events(df):
    flattened = [
        event 
        for sublist in df.apply(__split_one_termination, axis=1) 
        for event in sublist
    ]
    return pd.DataFrame(flattened)

def __split_one_termination(t):
    try:
        t = t.to_dict()
        if t['Type'] != 'Termination' or t['Subtype'] != 'Test':
            return [t]
        
        try:
            tests = t['Unit-Name'].strip('|').split('|')
            outcomes = t['Subsubtype'].strip('|').split('|')
            expandedevents = []
            for test, outcome in zip(tests, outcomes):
                newevent = copy.deepcopy(t)
                newevent['Unit-Name'] = test
                newevent['Subsubtype'] = outcome
                newevent['Unit-Type'] = 'Method'
                expandedevents.append(newevent)
        except AttributeError:
            return [t]
    except KeyError:
        logging.error('Missing some required keys to split termination event. Need \
            Type, Subtype, and Subsubtype. Doing nothing.')
        return [t] 

    return expandedevents

def _shouldwritekey(key, fieldnames):
    if not fieldnames:
        return True

    if key in fieldnames:
        return True

    return False

def maptouuids(sensordata=None, sdpath=None, uuids=None, uuidpath=None, crnfilter=None,
               crncol='crn', usercol='email', assignmentcol='CASSIGNMENTNAME', due_dates=None):
    """Map sensordata to users and assignments based on studentProjectUuids.

    Args:
        sensordata (pd.DataFrame): A DataFrame containing sensordata
        sdpath (str): Path to raw sensordata (CSV). Either this or `sensordata`
                      must be provided.
        uuids (pd.DataFrame): A DataFrame containined uuids
        uuidpath (str): Path to UUID file. The file is expected to contain columns
                        ['studentProjectUuid', {crncol}, {usercol}, {assignmentcol}]
                        at least. Either this or uuids must be provided.
        crnfilter (str): A CRN to filter UUIDs on
        crncol (str): Name of the column containing course CRNs
        assignmentcol (str): Name of the column containing assignment names. Defaults to
                             'CASSIGNMENTNAME'. This will get renamed to 'assignment'.
        usercol (str): Name of the column containing user information. This will get
                       renamed to userName, and domains will be removed from emails.
        due_dates (list): A list of `pd.Timestamp` values indicating due dates of assignments.
                          Use these timestamps as a heuristic identifier of which assignment
                          the events are being generated for. If omitted, the resulting
                          dataframe will have no **assignment** column.
    Returns:
       A `pd.DataFrame` containing the result of a left join on sensordata and uuids.
    """
    # check required params
    if sensordata is None and sdpath is None:
        raise ValueError('Either sensordata or sdpath must be provided. Got None for both.')
    if uuids is None and uuidpath is None:
        raise ValueError('Either uuids or uuidpath must be provided. Got None for both.')

    # read sensordata
    if sensordata is None:
        sensordata = pd.read_csv(sdpath, low_memory=False)

    # read uuids
    cols = ['userUuid', assignmentcol, usercol]
    if crnfilter:
        cols.append(crncol)
    if uuids is None:
        uuids = pd.read_csv(uuidpath, usecols=cols)
    uuids = (
        uuids.rename(columns={usercol: 'userName', assignmentcol: 'assignment'})
             .sort_values(by=['userName', 'assignment'], ascending=[1, 1])
    )
    umap = lambda u: u.split('@')[0] if str(u) != 'nan' and u != '' else u
    uuids['userName'] = uuids['userName'].apply(umap)

    # filter uuids by crn if provided
    if crnfilter:
        uuids = uuids[(uuids[crncol].notnull()) & (uuids[crncol].str.contains(crnfilter))]
        uuids = uuids.drop(columns=[crncol])

    # create user oracle
    uuids = (
            uuids.loc[:, ['userUuid', 'userName']]
                 .drop_duplicates(subset=['userUuid', 'userName'])
                 .set_index('userUuid')
    )

    # only map to assignments if we have reliable due_date data
    if due_dates:
        sensordata.loc[:, 'assignment'] = (
                sensordata['time'].apply(__assignment_from_timestamp, due_dates=due_dates)
        )

    # join
    merged = sensordata.join(uuids, on='userUuid')
    merged = merged.query('userName.notnull()')

    return merged

def __assignment_from_timestamp(t, due_dates, offset=pd.Timedelta(1, 'w')):
    t = pd.to_datetime(t, unit='ms')

    for idx, dd in enumerate(due_dates, start=1):
        if t < dd + offset:
            return 'Project {}'.format(idx)

    return None

def with_edit_sizes(df):
    """Given a data frame with Edit events containing Current-Sizes, group by
    Class-Name and return the dataframe with a column called 'edit_size', which
    contains the size of the edit made to the given file.
    """
    edits = df[(~df['Class-Name'].isna()) & (df['Type'] == 'Edit')] \
            .groupby(['userName', 'Class-Name']) \
            .apply(__get_edit_sizes)
    df.loc[df.index.isin(edits.index), 'edit_size'] = edits['edit_size']
    return df

def __get_edit_sizes(df):
    df['edit_size'] = df['Current-Size'].diff().abs().fillna(0)
    return df

