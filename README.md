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

### Description of Files
Some files have not been described here, because you can perform their functions using any data-processing software. So they are not really useful. The files described below will spit out CSV result files which you can put together for analysis based on your needs.

Running `./[file-name]` without any arguments will display usage information.

* [early_often.py](early_often.py) - Calculates early/often indices for solution code writing, test writing, normal program executions, and test code executions, along with a suite of other measures we use to try to assess incremental development.
* [incremental_checking.py](incremental_checking.py) - Calculates incremental checking and incremental test checking indices
* [time_spent.py](time_spent.py) - Calculates the time spent on each project in hours (using work session data)
* [subsessions.py](subsessions.py) - Reduces raw sensordata into subsessions. Subsessions are separated by program Launches
* [work_sessions.py](work_sessions.py) - Reduces subsession data into work sessions. Work sessions are separated by gaps of >= `THRESHOLD` hours without activity

[sensordata-utils.R](sensordata-utils.R) and [sensordata-figures.R](sensordata-figures.R) contain analysis and visualisation processes rather specific to our use cases, and without much re-use value that I can see. So I haven't described them here.
You may explore the source if you like.

The [visualisations](visualisations) directory contains tentative D3 visualisations of student programming habits over time.
