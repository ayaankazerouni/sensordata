#! /usr/bin/env python3
"""Import and consolidate incremental development metrics from several sources."""

import datetime
import pandas as pd
import numpy as np
import argparse

def consolidate_student_data(webcat_path=False, raw_inc_path=False,
                             time_path=False, launch_totals_path=False):
    """
    Import, format, and consolidate incremental development metrics from several sources.

    Args:
        webcat_path (str): String path, None for default, or False to omit
        raw_inc_path (str): String path, None for default, or False to omit
        time_path (str): String path, None for default, or False to omit
        launch_totals_path (str): String path to work_session data, None for default, or False to omit 
        repo_mining_path (str): String path, None for default, or False to omit 

    Returns:
        A DataFrame containing a row for each student-project, with metrics as columns.

    See also:
        :mod:`early_often`
        :mod:`incremental_checking`
        :mod:`time_spent`
    """
    if webcat_path is None:
        webcat_path = 'data/fall-2016/web-cat-students-with-sensordata.csv'

    if raw_inc_path is None:
        raw_inc_path = 'data/fall-2016/raw_inc.csv'

    if time_path is None:
        time_path = 'data/fall-2016/time_spent.csv'

    if launch_totals_path is None:
        launch_totals_path = 'data/fall-2016/work_sessions.csv'

    submissions = load_submission_data(webcat_path) # get webcat submission data

    merged = submissions

    if raw_inc_path:
        raw_inc_data = load_raw_inc_data(raw_inc_path) # get raw incremental programming data and format it
        merged = merged.merge(right=raw_inc_data, left_index=True, right_index=True)
    
    if time_path:
        time_data = load_time_spent_data(time_path) # get time spent on projects
        merged = merged.merge(right=time_data, left_index=True, right_index=True)
    
    if launch_totals_path:
        launch_totals = load_launch_totals(launch_totals_path) # get launch totals from work session data
        merged = merged.merge(right=launch_totals, left_index=True, right_index=True)
    
    if webcat_path and time_path:
        days_from_deadline = (merged['dueDateRaw'] - merged['projectStartTime'])
        merged['startedDaysFromDeadline'] = days_from_deadline.apply(lambda diff: diff.days)

    # drop identifying column if anonymized column was loaded for analysis
    if raw_inc_path:
        merged = merged.reset_index().set_index(['userId', 'assignment']).drop('userName', axis=1)

    return merged

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
