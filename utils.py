"""Convenience methods for common tasks, such as retrieiving
subsets of events, converting timestamps, getting a term, etc.

To use:
    import utils 
"""
import pandas as pd

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
    """Loads 'tangible' edit events.

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
