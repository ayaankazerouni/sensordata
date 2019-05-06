"""Splits events into work sessions, which are delimited by
a certain number of hours of inactivity.

See also:
    :mod:`subsessions`
"""
from datetime import datetime
import argparse
import pandas as pd

import utils

def summarise_worksessions(df):
    """Acts on sensordata for a single student-project.

    Returns a dataframe of work sessions, where work sessions are
    delimited by some hours of inactivity. This is typically called
    by :meth:`worksessions` as part of a split-apply-combine procedure.

    Args:
        df (DataFrame): containing all sensordata from the given project

    Returns:
        A *DataFrame* containing the work sessions for the given user on a given 
        assignment.
    """
    username, ws_id = df.name
    start_time = df['time'].min()
    end_time = df['time'].max()
    
    # launch info 
    normal_launches = df.query('Type == "Termination" and Subtype == "Normal"')
    test_launches = df.query('Type == "Termination" and Subtype == "Test"')
    outcomes = test_launches.apply(__test_outcomes, axis=1).agg('sum')

    # edit info
    edits = df[~df['edit_size'].isna()]
    test_edits = df[df['onTestCase'] == 1]['edit_size'].sum()
    normal_edits = df[df['onTestCase'] != 1]['edit_size'].sum()

    return pd.Series({
        'startTime': start_time,
        'endTime': end_time,
        'normalLaunches': normal_launches.shape[0],
        'testLaunches': test_launches.shape[0],
        'editSize': normal_edits,
        'testEditSize': test_edits
    })

def __test_outcomes(te):
    outcomes = te['Subsubtype'].strip('|').split('|')
    failures = outcomes.count('Failure')
    successes = outcomes.count('Success')
    errors = len(outcomes) - (failures + successes)

    return pd.Series({
        'successes': successes,
        'failures': failures,
        'errors': errors
    })
    
def assign_worksessions(df, threshold=1, milliseconds=True):
    """Assign work sessions to events, in a column called
    workSessionId.
    """
    delimit_hours = threshold * 3600
    if milliseconds:
        delimit_hours = delimit_hours * 1000 
    df['newSession'] = df['time'].diff() > delimit_hours # diff > threshold hrs?
    df['workSessionId'] = df['newSession'].cumsum().astype('int')
    return df

def worksessions(infile, outfile=None):
    """Given raw sensordata for all students, group events for
    individual student-projects and compute work sessions.

    Returns summarised work sessions, which includes start times,
    end times, the number of edits (test and normal) and the number of
    launches (test and normal).
    """
    df = pd.read_csv(infile, na_values=[], low_memory=False)

    df = df.sort_values(by=['userName', 'time'])
    df = utils.with_edit_sizes(df)

    print('Read {} events'.format(df.shape[0]))
    
    df = df.groupby(['userName']).apply(assign_worksessions) \
           .groupby(['userName', 'workSessionId']).apply(summarise_worksessions)

    return df
