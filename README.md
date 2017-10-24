# sensordata

A collection of scripts for pre-processing, analysis, and visualisation of SensorData collected by [DevEventTracker](https://github.com/web-cat/eclipse-plugins-importer-exporter/tree/DevEventTrackerAddition).

These scripts deal with data in CSV format.


If you use any of this work, please cite the following:

* [Ayaan M. Kazerouni, Stephen H. Edwards, T. Simin Hall, and Clifford A. Shaffer. 2017. DevEventTracker: Tracking Development Events to Assess Incremental Development and Procrastination.](https://dl.acm.org/citation.cfm?id=3059050&CFID=816451901&CFTOKEN=34061433)
* [Ayaan M. Kazerouni, Stephen H. Edwards, and Clifford A. Shaffer. 2017. Quantifying Incremental Development Practices and Their Relationship to Procrastination.](https://dl.acm.org/citation.cfm?id=3106180&CFID=816451901&CFTOKEN=34061433)

---

### Schema for Preprocessing Scripts (\*.py)
The data has the following fields:

* **time** (*required*) - UNIX timestamp in milliseconds
* **userId** (*required*) - A unique identifier for a user
* **projectId** (*required*) - A unique identifier for a user's project
* **CASSIGNMENTNAME** (*recommended*) - The name of the assignment
* **Type** (*required*) - [ Edit, Launch ] The type of event
* **Subtype** (*required for Launch events*) - [ Test, Normal ]
* **Subsubtype** (*required for `Unit-Type` = `Method` events*) - [ Add, Remove ] the action taken on the specified Unit
* **Unit-Type** - [ project, file, Class, Method, ... ] The type of unit affected in this event
* **Unit-Name** - The name of the `Unit` affected in this event

The following fields are **required** for *Edit* events (and can be `None` for other event types):
* **Class-Name** - The name of the class that originates the event
* **Current-Statements** - The number of statements in the originating file
* **Current-Methods** - The number of methods in the originating file
* **Current-Size** - The raw byte size of the originating file
* **Current-Test-Assertions** - The number of test assertions in the originating file
* **onTestCase** - [ 0, 1 ] Whether or not the event originates from a test file

### Description
#### Dependencies
All of the following depends on:
* [Python >= 3.5](https://docs.python.org/3.5/)
* [Numpy](http://www.numpy.org/)
* [Pandas](http://pandas.pydata.org/)
* [Node.js under LTS](https://github.com/nodejs/LTS)

#### Processes
Some files have not been described here. These files either do pretty basic stuff that can be done better in any data processing software, or are no longer dealing with current forms of the data.
They will be deleted soon.
The files described below will spit out results in CSV format.

Running `./[file-name]` without any arguments will display usage information.

* [early_often.py](early_often.py) - Calculates early/often indices for solution code writing, test writing, normal program executions, and test code executions, along with a suite of other measures we use to try to assess incremental development.
* [incremental_checking.py](incremental_checking.py) - Calculates incremental checking and incremental test checking indices
* [time_spent.py](time_spent.py) - Calculates the time spent on each project in hours (using work session data)
* [reference_test_gains.py](reference_test_gains.py) - Calculates growth rates of Web-CAT reference tests passed over time
* [subsessions.py](subsessions.py) - Reduces raw sensordata into subsessions. Subsessions are separated by program Launches
* [work_sessions.py](work_sessions.py) - Reduces subsession data into work sessions. Work sessions are separated by gaps of >= `THRESHOLD` hours without activity

[consolidate_sensordata.py](consolidate_sensordata.py) consolidates the results of all the above processes into a [Pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html) where each `student assignment` is a single row of scores and metrics. You can play with this data however you want in some kind [Jupyter](https://try.jupyter.org/) environment or export to CSV for more control.

[generate_project_report.py](generate_project_report.py) does **all the above processes** automatically, ending with the DataFrame of consolidated data.
Run `./generate_project_report.py --help` for usage info.

[sensordata-figures.R](sensordata-figures.R) does some pretty basic plotting rather specific to our use cases, and without much re-use value that I can see. So I haven't described it here.
You may explore the source if you like.

The [visualisations](visualisations) directory contains tentative D3.js visualisations of student programming habits over time.
