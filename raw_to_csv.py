#! /usr/bin/env python3
"""Author: Ayaan Kazerouni <ayaan@vt.edu>
Description: CLI tool to map raw URL events to CSV format,
while mapping events to users and assignments based on a uuid
file. Paths are hardcoded.

See also:
    :meth:`utils.maptouuids`
"""
import os
import glob

import pandas as pd
import utils

def __process_data_files(dirpath, dirname, resultpath): 
    datafilepath = os.path.join(dirpath, dirname)
    resultpath = os.path.join(dirpath, 'csv')
    os.mkdir(resultpath)

    fieldnames = utils.DEFAULT_FIELDNAMES + ['userUuid', 'studentProjectUuid', 'Set']
    fieldnames = [x for x in fieldnames if x not in ['email', 'CASSIGNMENTNAME']]
    
    for datfile in os.listdir(datafilepath):
        if os.path.isfile(os.path.join(datafilepath, datfile)):
            infile = os.path.join(datafilepath, datfile)
            print('Processing', datfile)
            utils.raw_to_csv(infile, '{}/{}.csv'.format(resultpath, datfile), fieldnames)
            print('=============')

    return resultpath

def __join_csvs(dirpath):
    df = pd.concat([
        pd.read_csv(f, low_memory=False) 
        for f 
        in glob.glob('{}/*.csv'.format(dirpath))
    ], ignore_index=True, sort=False)
    
    outpath = os.path.join('data', 'fall-2018', 'all.csv')
    
    # match with users and assignments
    uuidpath = os.path.join('data', 'fall-2018', 'cs3114uuids.csv')
    df = utils.maptouuids(sensordata=df, uuidpath=uuidpath)
    df = df.sort_values(by=['userName', 'assignment', 'time'], ascending=[1, 1, 1]) 
    
    # write out
    df.to_csv(outpath, index=False)


if __name__ == '__main__':
    cwd = os.getcwd()
    dirpath = os.path.join(cwd, 'data', 'fall-2018')
    dirname = 'data-files'
    resultpath = os.path.join(dirpath, 'csv')

    __process_data_files(dirpath, dirname, resultpath)
    __join_csvs(resultpath)
