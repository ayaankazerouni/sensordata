"""Separates events into subsessions, which are delimited by
termination events. So all events in a subsession take place
between consecutive terminations.

See also:
    :mod:`work_sessions`
"""
import csv
import sys

import pandas as pd

def summarise_subsession(sub):
    """Summarises events in a subsession in terms of code edits,
    test edits, and test launch outcomes.

    Must be called as the apply in a split-apply-combine procedure,
    grouping by users, work sessions, and subsessions.
    """
    _, _, subsession_name = sub.name # username, worksession, subsession

    if sub.empty:
        return None

    edits = sub[(sub['Type'] == 'Edit') & (~sub['Class-Name'].isna())]
    test_edits = edits[edits['onTestCase'] == 1]
    soln_edits = edits[edits['onTestCase'] != 1]
    
    try:
        launchTime = sub.loc[subsession_name, 'time']
        outcomes = sub.loc[subsession_name, 'Subsubtype']
        outcomes = outcomes.strip('|').split('|') if outcomes else []
        failures = outcomes.count('Failure')
        successes = outcomes.count('Success')
        errors = len(outcomes) - (failures + successes)
    except KeyError:
        # These events happened before the first launch
        failures, successes, errors = 0, 0, 0
        launchTime = None
    
    edits = (
        0 if edits.empty 
        else edits['edit_size'].sum()
    )

    test_edits = (
        0 if test_edits.empty
        else test_edits['edit_size'].sum()
    )

    soln_edits = (
        0 if soln_edits.empty
        else soln_edits['edit_size'].sum()
    )
        
    result = {
        'launchTime': launchTime,
        'testEdits': test_edits,
        'solnEdits': soln_edits,
        'testFailures': failures,
        'testSuccesses': successes,
        'testErrors': errors
    }

    return pd.Series(result)

def assign_subsessions(userevents, event_type='Termination'):
    """Assigns `subsessions` to events. A subsession contains 
    all the work done between two consecutive Termination events.

    Typically called as a part of a split-apply-combine procedure,
    grouping by users, assignments, and work sessions.

    Args:
        event_type (str, default=Termination): Delimit subsessions by
                        a specific kind of event. Defaults to termination
                        events.
    Returns:
        A DataFrame with a `subsession` column. The column should be
        treated as a nominal factor.
    """
    # Set the 'subsession' column to the index value of each delimiting event
    userevents.loc[
        (userevents.Type == event_type), 'subsession'
    ] = userevents.index[userevents.Type == event_type]

    # Forward fill from each termination
    userevents.subsession = ( 
        userevents
        .subsession
        .fillna(method='ffill')
        .fillna(-1) # for events that happened before the 1st delimiting event
    )

    return userevents
    
def main(args):
    infile = args[0]
    outfile = args[1]
    try:
        df = pd.read_csv(infile)
        result = df.groupby(['userName', 'workSessionId']).apply(assign_subsessions) \
                   .groupby(['userName',' workSessionId', 'subsession']).apply(summarise_subsession)
        result.to_csv(outfile, index=True)
    except FileNotFoundError as e:
        print("Error! File '{}' does not exist.".format(infile))
    except KeyError:
        print('Please ensure that work session ids were assigned before assigning subsessions.') 

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Clusters data into subsessions.\n\nSubsessions are separated by ' +
            'termination events.')
        print('Usage:\n\t./subsessions.py <input_file> <output_file>')
        sys.exit()
    main(sys.argv[1:])
