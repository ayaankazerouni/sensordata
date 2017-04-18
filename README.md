# sensordata

A collection of scripts for pre-processing, analysis, and visualisation of SensorData collected by [DevEventTracker](https://github.com/web-cat/eclipse-plugins-importer-exporter/tree/DevEventTrackerAddition).

These scripts deal with data in CSV format.

---

### Schema for Preprocessing Scripts (\*.py)
The data has the following fields:

* **time** (*required*) - UNIX timestamp in milliseconds
* **userId** (*required*) - A unique identifier for a user
* **projectId** (*required*) - A unique identifier for a user's project
* **CASSIGNMENTNAME** (*recommended*) - The name of the assignment
* **Class-Name** (*required for Edit events*) - The name of the class the event takes place on
* **Unit-Type** - [ project, file, Class, Method, ... ] The type of unit affected in this event
* **Unit-Name** - The name of the Unit affected in this event
* **Type** (*required*) - [ Edit, Launch ] The type of event
* **Subtype** (*required for Launch events*) - [ Test, Normal ]
* **Subsubtype** (*required for Unit-Type = Method events*) - [ Add, Remove ] the action taken on the specified Unit
* **onTestCase** (*required for Edit events*) - [ 0, 1 ]

### Description of Processes
Some python files have not been described here, because you can perform their functions using any data-processing software. So they are not really useful.

* [early_often.py](early_often.py) - Calculates early/often indices for solution code writing, test writing, normal program executions, and test code executions, along with a suite of other measures we use to try to assess incremental development.
* [incremental_checking.py](incremental_checking.py) - Calculates incremental checking and incremental test checking indices
* [subsessions.py](subsessions.py) - Reduces raw sensordata into subsessions. Subsessions are separated by program Launches
* [work_sessions.py](work_sessions.py) - Reduces subsession data into work sessions. Work sessions are separated by gaps of >= 3 hours without activity
* [time_spent.py](time_spent.py) - Calculates the time spent on each project in hours (using work session data)

[sensordata-utils.R](sensordata-utils.R) and [sensordata-figures.R](sensordata-figures.R) contain analysis and visualisation processes rather specific to my research, so I haven't described them here.
You may explore the source if you like.

The [visualisations](visualisations) directory contains tentative D3 visualisations of student programming habits over time. These will probably go away soon.
