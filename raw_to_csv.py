#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:09:43 2018

@author: ayaan
"""
# In[]
import pandas as pd
import csv
import sys
from os.path import expanduser
sys.path.append('%s/Developer/' % expanduser('~'))
from sensordata import early_often
from urllib import parse

FIELDNAMES=[
    'uri',
    'studentProjectUuid',
    'userUuid',
    'time',
    'Line',
    'Type',
    'Set',
    'Subtype'
]

def raw_to_csv(filepath):
    with open(filepath, 'r') as infile, open('data/fall-debug.csv', 'w') as fallout, \
        open('data/spring-debug.csv', 'w') as springout:
        
        fallwriter = csv.DictWriter(fallout, delimiter=',', fieldnames=FIELDNAMES)
        springwriter = csv.DictWriter(springout, delimiter=',', fieldnames=FIELDNAMES)
        
        fallwriter.writeheader()
        springwriter.writeheader()
        
        for index, line in enumerate(infile):
            if (index % 1000000 == 0):
                p = float(("%0.2f"%(index * 100 / 8524823)))
                print('Processed %s of file' % p)
            event = processline(line)
            if event is not None:
                term = early_often.get_term(event['time'])
                try:
                    if term.startswith('fall'):
                        fallwriter.writerow(event)
                    elif term.startswith('spring'):
                        springwriter.writerow(event)
                except ValueError:
                    print("Line {0}".format(line))
                    sys.exit(0) 

# In[]
def processline(line):
    line = line.split(':', 1)[-1]
    items = parse.parse_qs(parse.urlparse(line).query)
    kvpairs = {}
    for key, value in items.items():
        if key in FIELDNAMES: 
            kvpairs[key] = value[0].rstrip('\n\r')
        elif key.startswith('name'):
            k = value[0]
            v = items['value%s' % key[-1]][0]
            kvpairs[k] = v.rstrip('\n\r')
    kvpairs['time'] = int(float(kvpairs['time'])) / 1000
    if kvpairs['Type'] != 'Debug':
        return None
    return kvpairs

# In[]
def maptousers(debuggerpath, uuidspath, crns):
    debug = pd.read_csv(debuggerpath, low_memory=False).fillna('')
    uuids = pd.read_csv(uuidspath).fillna('')
    
    uuids = uuids.rename(columns={'project uuid': 'studentProjectUuid', 'user uuid': 'userUuid', \
                                  'assignment name': 'assignment', 'email': 'userName'}) \
        .drop(columns=['project id', 'course', 'uri']) \
        .set_index(keys=['userUuid', 'studentProjectUuid']) \
        .query('CRN in @crns')
        
    uuids['userName'] = uuids['userName'].apply(lambda u: u.split('@')[0] if u != '' else u)
    
    debug = debug.set_index(keys=['userUuid', 'studentProjectUuid'])
    return debug.merge(right=uuids, right_index=True, left_index=True) \
        .reset_index().set_index(keys=['userName', 'assignment'])
