"""Import datasets and metrics from several sources."""
import datetime
import pandas as pd
import numpy as np
import argparse

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

def load_submission_dists(webcat_path, **kwargs):
    """Return a description of each students distribution of submission scores for
    each assignment, as a four number summary (quartiles).
    
    Each student has a variable number of submissions, and each receives score between
    0 and 1. Typically our median final score is high (around 92%), indicating that students
    eventually "get there" in terms of project completion. The distribution of scores for an
    assignment is more informative.

    Args:
        webcat_path (str): Path to a CSV file containing Web-CAT submission results
        **kwargs: Keyword-arguments passed to :meth:`load_submission_data`

    Returns:
        A DataFrame containing four columns (quartiles) for each submission.

    See also:
        :meth:`load_submission_data`

    Note:
        If `onlyfinal` is specified in \*\*kwargs, it will be ignored and forced to **False**. 
    """
    if 'onlyfinal' in kwargs: # Can't get a distribution from one submission  
        del kwargs['onlyfinal']

    submissions = load_submission_data(webcat_path=webcat_path, onlyfinal=False, **kwargs)
    return submissions.groupby(['userName', 'assignment']).agg({'score': [
        ('Q1', lambda s: np.quantile(s, q=0.25)),
        ('Q2', np.median),
        ('Q3', lambda s: np.quantile(s, q=0.75)),
        ('Q4', np.max)
    ]}).loc[:, 'score']

def load_raw_inc_data(raw_inc_path):
    """Loads early/often metrics for code editing and launching.
    
    Note that this does NOT calculate the metrics. raw_inc_path refers
    to a CSV file that contains already-calculated values. 
    """

    data = pd.read_csv(raw_inc_path)

    # each derived metric is calculated once using changes in raw file size, and once using change in statements
    data['byteTestWriting'] = data['solutionByteEarlyOftenIndex'] - data['testByteEarlyOftenIndex']
    data['byteTestChecking'] = data['solutionByteEarlyOftenIndex'] - data['testLaunchEarlyOften']
    data['byteNormalChecking'] = data['solutionByteEarlyOftenIndex'] - data['normalLaunchEarlyOften']
    data['byteChecking'] = data['solutionByteEarlyOftenIndex'] - data['launchEarlyOften']
    data['byteSkew'] = 3 * (data['byteEarlyOftenIndex'] - data['byteEditMedian']) / data['byteEditSd']
    data['solutionByteSkew'] = 3 * (data['solutionByteEarlyOftenIndex'] - data['solutionByteEditMedian']) / \
        data['solutionByteEditSd']
    data['testByteSkew'] = 3 *(data['testByteEarlyOftenIndex'] - data['testByteEditMedian']) / data['testByteEditSd']

    data['stmtTestWriting'] = data['solutionStmtEarlyOftenIndex'] - data['testStmtsEarlyOftenIndex']
    data['stmtTestChecking'] = data['solutionStmtEarlyOftenIndex'] - data['testLaunchEarlyOften']
    data['stmtNormalChecking'] = data['solutionStmtEarlyOftenIndex'] - data['normalLaunchEarlyOften']
    data['stmtChecking'] = data['solutionStmtEarlyOftenIndex'] - data['launchEarlyOften']
    data['stmtSkew'] = 3 * (data['stmtEarlyOftenIndex'] - data['stmtEditMedian']) / data['stmtEditSd']

    data['launchSkew'] = 3 * (data['launchEarlyOften'] - data['launchMedian']) / data['launchSd']
    data['testLaunchSkew'] = 3 * (data['testLaunchEarlyOften'] - data['testLaunchMedian']) / data['testLaunchSd']
    data['normalLaunchSkew'] = 3 * (data['normalLaunchEarlyOften'] - data['normalLaunchMedian']) / data['normalLaunchSd']
    data.rename(index=str, columns={'email': 'userName'}, inplace=True)
    data['userName'].fillna('', inplace=True)
    data['userName'] = data['userName'].apply(lambda x: x if x == '' else x[:x.index('@')])
    data.sort_values(by=['assignment', 'userName'], inplace=True)

    data.set_index(['userName', 'assignment'], inplace=True)

    return data

def load_submission_data(webcat_path, onlyfinal=True, pluscols=[], keepassignments=[]):
    """Loads submission data from webcat_path, which points at a
    CSV file containing submission data from a Web-CAT server.
     
    Submission data is modified so that score.correctness only represents 
    scores on instructor-written reference tests, and doesn't include points
    from students' own tests.
    
    Args:
        webcat_path (str): Path to web-cat submission data. 
        onlyfinal (bool, optional): Return only the last submission for each student-project?
            Defaults to True
        pluscols (list, optional): Columns to load from raw CSV in addition to correctness, code
            coverage, and submission time data. Defaults to an empty list
        keepassignments (list, optional): Assignment names to load submissions for. If empty, load
            submissions for all assignments

    Returns:
        A DataFrame containing submission results for each student on each assignment.
    """
    cols_of_interest = [
        'userName',
        'assignment',
        'submissionNo',
        'score.correctness',
        'max.score.correctness',
        'elements',
        'elementsCovered',
        'submissionTimeRaw',
        'dueDateRaw'
    ] + pluscols
    date_parser = lambda d: datetime.datetime.fromtimestamp(int(float(d)) / 1000)
    data = pd.read_csv(webcat_path, \
        usecols=cols_of_interest, \
        parse_dates=['dueDateRaw', 'submissionTimeRaw'], \
        date_parser=date_parser)
    if keepassignments:
        data = data.query('assignment in @keepassignments')
    data = data.sort_values(by=['assignment', 'userName', 'submissionNo'], ascending=[1,1,0])

    if onlyfinal:
        # get the last submission from each user on each project
        data.drop_duplicates(subset=['assignment', 'userName'], keep='first', inplace=True)

    # calculate reftest percentages and discretised project grades
    data.loc[:, 'score.correctness'] = data['score.correctness'] / data['max.score.correctness']
    data.loc[:, 'elementsCovered'] = (data['elementsCovered'] / data['elements']) / 0.98
    data.loc[:, 'elementsCovered'] = data['elementsCovered'].apply(lambda x: x if x <= 1 else 1)
    data.loc[:, 'score'] = data['score.correctness'] / data['elementsCovered']
    data.loc[:, 'score'] = data['score'].apply(lambda x: x if x <= 1 else 1)

    data.drop(columns=['score.correctness'], inplace=True)

    # calculate submission time outcomes 
    hours_from_deadline = (data['dueDateRaw'] - data['submissionTimeRaw'])
    data.loc[:, 'finishedHoursFromDeadline'] = hours_from_deadline.apply(lambda diff: diff.total_seconds() / 3600)
    data.loc[:, 'onTimeSubmission'] = data['finishedHoursFromDeadline'].apply(lambda h: 1 if h >= 0 else 0)

    data.set_index(['userName', 'assignment'], inplace=True)
    return data

def load_time_spent_data(time_path):
    """Loads the time spent in hours for each student-project."""

    cols_of_interest = [
        'email',
        'assignment',
        'hoursOnProject',
        'projectStartTime'
    ]
    date_parser = lambda d: datetime.datetime.fromtimestamp(int(float(d)) / 1000)
    data = pd.read_csv(time_path, usecols=cols_of_interest, parse_dates=['projectStartTime'], date_parser=date_parser)
    data.rename(index=str, columns={'email': 'userName'}, inplace=True)
    data['userName'].fillna('', inplace=True)
    data['userName'] = data['userName'].apply(lambda x: x if x == '' else x[:x.index('@')])
    data.sort_values(by=['assignment', 'userName'], ascending=[1, 1], inplace=True)
    data.set_index(['userName', 'assignment'], inplace=True)

    return data

