"""Convenience methods for common tasks, such as retrieiving
subsets of events, converting timestamps, getting a term, etc.

To use:
    import utils 
"""
import pandas as pd
import csv
from urllib import parse

def load_launches(launch_path=None, sensordata_path=None):
    """Loads raw launch data.

    Convenience method: filters out everything but Launches from raw sensordata,
    or reads launches from an already filtered CSV file. If both are specified,
    the launch_path will be given precedence.
    """
    if not launch_path and not sensordata_path:
        raise ValueError("Either launch_path or sensordata_path must be specified and non-empty.")

    if launch_path:
        try:
            launches = pd.read_csv(launch_path) # no need to do any formatting, either
            return launches
        except FileNotFoundError:
            if not sensordata_path:
                return None # nothing at launch_path, sensordata_path was not specified

    dtypes = {
        'email': str,
        'CASSIGNMENTNAME': str,
        'time': float,
        'Type': str,
        'Subtype': str,
        'TestSucesses': str,
        'TestFailures': str
    }
    eventtypes = ['Launch', 'Termination']
    data = pd.read_csv(sensordata_path, 
        dtype=dtypes, usecols=dtypes.keys()) \
        .query('Type in @eventtypes') \
        .rename(columns={ 
            'email': 'userName', 
            'CASSIGNMENTNAME': 'assignment', 
            'TestSucesses': 'TestSuccesses'
		})
    data.userName = data.userName.apply(lambda u: u.split('@')[0])
    data = data.set_index(['userName', 'assignment'])
    return data

def get_term(timestamp):
    """Returns a term id based on a timestamp in seconds."""
    try:
        eventtime = datetime.datetime.fromtimestamp(timestamp)
        year = eventtime.year
        month = eventtime.month

        if month >= 8:
            return 'fall%d' % year
        elif month >= 7: # TODO: Deal with summer terms?
            return 'summer-1-%d' % year
        elif month > 5:
            return 'summer-2-%d' % year
        elif month >= 1:
            return 'spring%d' % year
        else:
            return None
    except ValueError:
        print('Error! Please make sure your timestamp is in seconds.')
        sys.exit()

def load_edits(edit_path=None, sensordata_path=None):
    """Loads edit events that took place on a source file. 

    This convenience method filters out Edit events from raw sensordata, or
    reads an already filtered CSV file. If both edit_path and sensordata_path
    are specified, the already-filtered file (at edit_path) takes precedence.
    """
    if not edit_path and not sensordata_path:
        raise ValueError("Either edit_path or sensordata_path must be specified and non-empty")

    if edit_path:
        try:
            edits = pd.read_csv(edits) # no formatting needed
            return edits
        except FileNotFoundError:
            if not sensordata_path:
                raise ValueError("edit_path is invalid and sensordata_path not specified.")
    
    # edit_path was invalid, so we need to get edit events from all sensordata
    dtypes = {
        'email': str,
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
    data = pd.read_csv(sensordata_path, dtype=dtypes, usecols=dtypes.keys())
    data = data[(data['Type'] == 'Edit') & (data['Class-Name'] != '')]
    data = (
            data
            .fillna('')
            .sort_values(by=['email', 'CASSIGNMENTNAME', 'time'], ascending=[1,1,1])
            .rename(columns={ 'email': 'userName', 'CASSIGNMENTNAME': 'assignment' })
        )
    data['userName'] = data.userName.apply(lambda u: u.split('@')[0])
    data = data.set_index(['userName', 'assignment'])
    return data

def raw_to_csv(inpath, outpath, fieldnames=None):
    """
    Given a file of newline separated URLs, writes the URL query params as
    rows in CSV format to the specified output file.

    If your URLs are DevEventTracker posted events, then you probably want the following default fieldnames:
    fieldnames = [ 
        email,
        CASSIGNMENTNAME,
        time,
        Class-Name,
        Unit-Type,
        Type,
        Subtype,
        Subsubtype,
        onTestCase,
        Current-Statements,
        Current-Methods,
        Current-Size,
        Current-Test-Assertions 
    ]
    """
    with open(inpath, 'r') as infile, open(outpath, 'w') as outfile:
        if not fieldnames:
            fieldnames = [ 
                'email',
                'CASSIGNMENTNAME',
                'time',
                'Class-Name',
                'Unit-Type',
                'Type',
                'Subtype',
                'Subsubtype',
                'onTestCase',
                'Current-Statements',
                'Current-Methods',
                'Current-Size',
                'Current-Test-Assertions'
            ]
        writer = csv.DictWriter(fallout, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()
             
        for index, line in enumerate(infile):
            if (index % 1000000 == 0):
                p = float(("%0.2f"%(index * 100 / 8524823)))
                print('Processed %s of file' % p)
            event = processline(line)
            if event is not None:
                writer.writerow(event)

def processline(url, fieldnames=None, filtertype=None):
    """
    Given a URL, returns a dict object containing the key-value
    pairs from its query params. Filters for a specific Type if specified.

    Keyword arguments:
    filtertype  =   Only return a dict if the query param for Type == filtertype
    """
    url = url.split(':', 1)[-1]
    items = parse.parse_qs(parse.urlparse(url).query)
    kvpairs = {}
    for key, value in items.items():
        if _shouldwritekey(key, fieldnames): 
            kvpairs[key] = value[0].rstrip('\n\r')
        elif key.startswith('name'): # some items are in the form name0=somekey, value0=somevalue
            k = value[0]
            v = items['value%s' % key[-1]][0]
            if _shouldwritekey(k, fieldnames): 
                kvpairs[k] = v.rstrip('\n\r')
    kvpairs['time'] = int(float(kvpairs['time'])) / 1000 # time will always be written
    if filtertype and kvpairs['Type'] != filtertype:
        return None
    return kvpairs

def _shouldwritekey(key, fieldnames):
    if not fieldnames:
       return True
    elif key in fieldnames:
       return True
    else:
       return False

def _maptousers(debuggerpath, uuidspath, crns):
    debug = pd.read_csv(debuggerpath, low_memory=False).fillna('')
    uuids = pd.read_csv(uuidspath).fillna('')
    
    uuids = uuids.rename(columns={'project uuid': 'studentProjectUuid', 'user uuid': 'userUuid', \
                                  'assignment name': 'assignment', 'email': 'userName'}) \
        .drop(columns=['project id', 'course', 'uri']) \
        .set_index(keys=['userUuid', 'studentProjectUuid']) \
        .query('CRN in @crns')
        
    uuids['userName'] = uuids['userName'].apply(lambda u: u.split('@')[0] if u != '' else u)
    
    debug = debug.set_index(keys=['userUuid', 'studentProjectUuid'])
    return debug.merge(right=uuids, right_index=True, left_index=True) \
        .reset_index().set_index(keys=['userName', 'assignment'])
