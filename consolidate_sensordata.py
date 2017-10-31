"""Import and consolidate incremental development metrics from several sources."""

import datetime
import pandas as pd

from method_metrics import get_method_metrics

def consolidate_student_data(webcat_path=None, raw_inc_path=None,
                             time_path=None, ref_test_gains_path=None, ws_path=None,
                             repo_mining_path=None):
    """
    Import, format, and consolidate incremental development metrics from several sources.

    Keyword arguments:
    webcat_path         = path to webcat submission data
    raw_inc_path        = path to raw incremental development scores
    time_path           = path to time spent data
    ref_test_gains_path = path to ref_test_gains metrics
    ws_path             = path to work session data (for launch totals)
    repo_mining_path    = path to repo-mining results from repodriller
    """
    if webcat_path is None:
        webcat_path = 'data/fall-2016/web-cat-students-with-sensordata.csv'

    if raw_inc_path is None:
        raw_inc_path = 'data/fall-2016/raw_inc.csv'

    if time_path is None:
        time_path = 'data/fall-2016/time_spent.csv'

    if ref_test_gains_path is None:
        ref_test_gains_path = 'data/fall-2016/ref_test_gains.csv'

    if ws_path is None:
        ws_path = 'data/fall-2016/work_sessions.csv'

    if repo_mining_path is None:
        repo_mining_path = 'data/repo-mining.csv'

    webcat_data = __load_webcat_submission_data(webcat_path) # get webcat submission data
    ref_test_gains = __load_ref_test_data(ref_test_gains_path) # get ref-test-gains data and format it
    raw_inc_data = __load_raw_inc_data(raw_inc_path) # get raw incremental programming data and format it
    time_data = __load_time_spent_data(time_path) # get time spent on projects
    launch_totals = __load_launch_totals(ws_path) # get launch totals from work session data
    method_metrics = get_method_metrics(repo_mining_path) # get aggregated repo-mining metrics

    merged = webcat_data.merge(right=ref_test_gains, left_index=True, right_index=True) \
        .merge(right=raw_inc_data, left_index=True, right_index=True) \
        .merge(right=time_data, left_index=True, right_index=True) \
        .merge(right=launch_totals, left_index=True, right_index=True) \
        .merge(right=method_metrics, left_index=True, right_index=True)

    days_from_deadline = (merged['dueDateRaw'] - merged['projectStartTime'])
    merged['startedDaysFromDeadline'] = days_from_deadline.apply(lambda diff: diff.days)

    # drop identifying column
    merged = merged.reset_index().set_index(['userId', 'assignment']).drop('userName', axis=1)

    return merged

def __load_webcat_submission_data(webcat_path):
    """
    Loads webcat submission data from webcat_path. Only returns the student's final submission
    on each projects. Submission data is modified so that score.correctness
    only represents scores on instructor-written reference tests.
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
    ]
    date_parser = lambda d: datetime.datetime.fromtimestamp(int(float(d)) / 1000)
    data = pd.read_csv(webcat_path, \
        usecols=cols_of_interest, \
        parse_dates=['dueDateRaw', 'submissionTimeRaw'], \
        date_parser=date_parser)
    data.sort_values(by=['assignment', 'userName', 'submissionNo'], ascending=[1,1,0], inplace=True)

    # get the last submission from each user on each project
    data.drop_duplicates(subset=['assignment', 'userName'], keep='first', inplace=True)

    # calculate reftest percentages and discretised project grades
    data['score.correctness'] = data['score.correctness'] / data['max.score.correctness']
    data['elementsCovered'] = (data['elementsCovered'] / data['elements']) / 0.98
    data['elementsCovered'] = data['elementsCovered'].apply(lambda x: x if x <= 1 else 1)
    data['score.reftest'] = data['score.correctness'] / data['elementsCovered']

    #  calculate submission time outcomes
    hours_from_deadline = (data['dueDateRaw'] - data['submissionTimeRaw'])
    data['finishedHoursFromDeadline'] = hours_from_deadline.apply(lambda diff: diff.total_seconds() / 3600)
    data['onTimeSubmission'] = data['finishedHoursFromDeadline'].apply(lambda h: 1 if h >= 0 else 0)

    data.set_index(['userName', 'assignment'], inplace=True)
    return data

def __load_ref_test_data(ref_test_gains_path):
    cols_of_interest = [
        'assignment',
        'userName',
        'dropCount',
        'flatCount',
        'flatPercent',
        'gainCount',
        'gainEarlyOften',
        'gainPercent'
    ]
    data = pd.read_csv(ref_test_gains_path, usecols=cols_of_interest)
    data['jitterGain'] = data['gainCount'] / (data['gainCount'] + data['dropCount'])
    data.set_index(['userName', 'assignment'], inplace=True)

    return data

def __load_raw_inc_data(raw_inc_path):
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

def __load_time_spent_data(time_path):
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

def __load_launch_totals(ws_path):
    cols_of_interest = [
        'email',
        'CASSIGNMENTNAME',
        'normalLaunches',
        'testLaunches'
    ]
    data = pd.read_csv(ws_path, usecols=cols_of_interest)
    data.rename(index=str, columns={'CASSIGNMENTNAME': 'assignment', 'email': 'userName'}, inplace=True)
    data['userName'].fillna('', inplace=True)
    data['userName'].unique()
    data['userName'] = data['userName'].apply(lambda x: x if x == '' else x[:x.index('@')])
    data = data.groupby(['userName', 'assignment'])[['testLaunches', 'normalLaunches']].sum()
    data = data.reset_index().set_index(['userName', 'assignment'])

    return data

MERGED = consolidate_student_data()
