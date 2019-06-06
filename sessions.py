"""Splits events into sessions based on different delimiting
criteria.

Worksessions:
    These are delimited by a certain amount of time of inactivity.
    See :meth:`assign_worksessions`

Subsessions:
    These are delimited by events of interest.
    See :meth:`assign_subsessions`
"""
from datetime import datetime
import pandas as pd

import utils
    
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

def assign_subsessions(userevents, event_type='Termination', forward=True):
    """Assigns `subsessions` to events. A subsession contains 
    all the work done after or before an event of interest, until
    another event of interest is reached.

    By default subsessions are computing in the forward direction,
    e.g., all the work done *after* a Launch is grouped together. This
    affects whether "orphan" events will be at the head or tail of the
    event stream.

    Typically called as a part of a split-apply-combine procedure,
    grouping by users, assignments, and work sessions.

    Args:
        event_type (list or str): Delimit subsessions by a specific kind of 
            event; defaults to termination events. If a list, delimits subsessions
            by all the specified event Types.
        forward (bool): Compute subsessions forward or backward?
    Returns:
        A DataFrame with a `subsession` column. The column should be
        treated as a nominal factor.
    """
    # Need events in chronological order to assign subsessions 
    userevents = userevents.sort_values(by=['time'], ascending=[1])

    if isinstance(event_type, str):
        event_type = [event_type]
    
    # mark each relevant event as a subsession delimiter
    userevents.loc[
        (userevents.Type.isin(event_type)), 'subsession'
    ] = userevents.index[userevents.Type.isin(event_type)]

    # Forward fill from each termination
    direction = 'ffill' if forward else 'bfill'
    userevents.subsession = ( 
        userevents
        .subsession
        .fillna(method=direction)
        .fillna(-1) # for events that happened before the 1st delimiting event (or after the last)
    )
    userevents.loc[:, 'subsession'] = userevents['subsession'].astype(int)

    return userevents.drop(columns=['userName'])

