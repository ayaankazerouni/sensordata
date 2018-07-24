import time
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Setup items
pd.options.display.float_format = '{:.2f}'.format

DEBUGPATH = 'data/fall-2016/debugger-use.csv'

def countbreakpointsession(sessions):
    """Count the number of debugger sessions that included at least one Breakpoint.
    
    Takes a dataframe of summarised debugger sessions as input.
    """
    return len(sessions.query('hitBreakpoints > 0'))

def timespentdebugging(sessions):
    """Count the time spent debugging on each project.
    
    Takes a dataframe of summarised debugger sessions as input. 
    """
    return np.sum((session.endTime - session.time).total_seconds()) / 3600

def dateparser(d, s=True): 
    """Parse timestamps

    Keyword arguments:
        s   True if timestamps are in seconds, False otherwise
    """
    if s:
        return datetime.fromtimestamp(int(float(d)))
    else:
        return datetime.fromtimestamp(int(float(d / 1000)))

def sessionsummary(session):
    """Get a summary for a single debug session.

    Includes the start time, end time, and number of breakpoints and steps.
    """
    if len(session) > 0:
        counts = session['Subtype'].value_counts()
        bpset = len(session.query("Set == 'set'"))
        bphit = counts.get('Breakpoint', 0)
        stepover = counts.get('Step over', 0)
        stepinto = counts.get('Step into', 0)
        starttime = session.iloc[0].time
        endtime = session.iloc[-1].time
    else:
        bpset = bphit = stepover = stepinto = starttime = endtime = 0

    result = {
        'time': starttime, # call it 'time' so we can concat with other data
        'endTime': endtime,
        'setBreakpoints': bpset,
        'hitBreakpoints': bphit,
        'stepOver': stepover,
        'stepInto': stepinto
    }
    return pd.Series(result)


def userdebugsessions(userevents):
    """Given all Debug events from a student on a project, 
    organise them into debug sessions and summarise. 
    """
    userevents.loc[userevents.Subtype == 'Terminate', 'session'] = userevents.index[userevents.Subtype == 'Terminate']
    userevents.session = (
        userevents.session
        # fill backwards from termination
        .fillna(method='bfill')
        # fills operations after the last termination
        .fillna(method='ffill')
        # fills -1 if there were no start/terminate events
        .fillna(-1)
    )

    sessions = userevents.groupby(['session']).apply(sessionsummary) 
    return sessions

def getdebugsessions(debugpath):
    """Given raw Debug events for all students on all projects, 
    reduce them to session summaries for each student-project
    """
    dtypes = {
        'userName': str,
        'assignment': str,
        'time': float,
        'Line': str,
        'Set': str,
        'Type': str,
        'Subtype': str
    }
    assignments = [ 'Project 1', 'Project 2', 'Project 3', 'Project 4' ]
    events = pd.read_csv(filepath_or_buffer=debugpath, low_memory=False, date_parser=dateparser,
        parse_dates=['time'], dtype=dtypes, usecols=dtypes.keys()) \
        .query("Subtype != 'Unknown' and assignment in @assignments") \
        .sort_values(['userName', 'assignment', 'time'], ascending=[1, 1, 1])
    sessions = events.groupby(['userName', 'assignment']).apply(userdebugsessions)

    return sessions
