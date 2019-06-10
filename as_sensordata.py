"""Helper methods for converting event data from other sources
to the DevEventTracker format. Typically you would do this to allow
interpersing different event types (e.g. Submissions, method
modifications, etc.) into a larger set of DevEventTracker events. 
"""
import pandas as pd
import load_datasets

def method_mods_to_edits(df=None, filepath=None, testonly=False):
    """Convert method modification events, as emitted by the
    project at https://github.com/ayaankazerouni/incremental-testing,
    to the sensordata format.

    Args:
        df (pd.DataFrame): A dataframe of method modification events
        filepath (str): Path to a CSV file containing method modification 
                        events
        testonly (bool): Only convert and return changes to test methods?

    Returns:
        The same DataFrame, possibly with only test changes, with columns
        in the sensordata format (see :attr:`utils.DEFAULT_FIELDNAMES`).
    """
    if df is None and filepath is None:
        raise ValueError('Either df or filepath must be specified.')

    if df is None:
        df = pd.read_csv(filepath)
    
    if testonly:
        df = df[df['Type'] == 'MODIFY_TESTING_METHOD']

    df = df.apply(__sensordata_from_method_mod, axis=1) \
           .drop_duplicates(subset=['userName', 'assignment', 'time', 
               'Class-Name', 'Unit-Name', 'edit_size'])
    return df

def __sensordata_from_method_mod(mod):
    modtype = mod['Type']
    method_id = mod['methodId']
    on_test_case = 0
    if modtype == 'MODIFY_TESTING_METHOD':
        on_test_case = 1
        method_id = mod['testMethodId']

    class_name = method_id.split(',')[0]
    method_name = method_id.split(',')[1]

    return pd.Series({
        'userName': mod['userName'],
        'Type': 'Edit',
        'Subtype': 'Commit',
        'Unit-Name': method_name,
        'Unit-Type': 'Method',
        'Class-Name': class_name,
        'studentProjectUuid': mod['project'],
        'commitHash': mod['commitHash'],
        'edit_size': mod['modsToMethod'],
        'assignment': mod['assignment'],
        'time': mod['time'],
        'onTestCase': on_test_case
    })

def submissions_to_sensordata(df=None, submissionpath=None, **kwargs):
    """Convert submissions to the DevEventTracker format.

    Args:
        df (pd.DataFrame): A DataFrame of submissions, as returned 
            by :meth:`load_datasets.load_submission_data`
        submissionpath (str): A path to a CSV containing submission information
        kwargs (dict): Other keyword arguments passed to :meth:`load_datasets.load_submission_data`
    Returns:
        The submissions in the same format as DevEventTracker data
    """
    if df is None and submissionpath is None:
        raise ValueError('Either df or submissionpath must be specified.')

    if df is None:
        onlyfinal = kwargs.get('onlyfinal', True)
        pluscols = kwargs.get('pluscols', [])
        df = load_datasets.load_submission_data(webcat_path=submissionpath, onlyfinal=onlyfinal, 
                                                         pluscols=pluscols)

    return df.reset_index().apply(__sensordata_from_sub, axis=1)

def __sensordata_from_sub(sub):
    return pd.Series({
        'userName': sub['userName'],
        'Type': 'Submission',
        'Subtype': sub['submissionNo'],
        'assignment': sub['assignment'],
        'time': sub['submissionTimeRaw'],
        'score': sub['score'],
        'elementsCovered': sub['elementsCovered']
    })

