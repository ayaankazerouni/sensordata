# sensordata

A collection of scripts for measuring and visualising aspects of incremental software development, using SensorData collected by [DevEventTracker](https://github.com/web-cat/eclipse-plugins-importer-exporter/tree/DevEventTrackerAddition).

The following paper details some of the measures described here:

* [Ayaan M. Kazerouni, Stephen H. Edwards, and Clifford A. Shaffer. 2017. Quantifying Incremental Development Practices and Their Relationship to Procrastination.](https://people.cs.vt.edu/ayaan/assets/publications/p191-kazerouni.pdf)

---

* [Documentation](https://ayaankazerouni.github.io/sensordata)
* [Assumed schema](#assumed-schema)
* [Dependencies](#dependencies)
* [JS visualisations](#js-visualisations)
  - [Skyline plots](#skyline-plots)

### Assumed schema
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
* [Python >= 3.5](https://docs.python.org/3.5/)
* [Numpy](http://www.numpy.org/)
* [Pandas](http://pandas.pydata.org/)
* [Node.js under LTS](https://github.com/nodejs/LTS) (for visualisations)

#### JS visualisations
The [visualisations](visualisations) directory contains **tentative** D3.js visualisations of student programming habits over time.
To get things working you should:
* `npm install`
* Point the method calls in [main.js](visualisations/src/main.js) at a data file

Note that all visualisations assume that they are being given data for a _single student_ on a _single project_, since the purpose of these figures are for eventual use in a learning dashboard for the student.

##### Skyline Plots
Data format (work session data):
* start time (milliseconds)
* end time (milliseconds)
* number of test edits
* number of solution edits

You would also need some due date data (see [dueTimes.js](visualisations/dueTimes.js)) to show milestone markers.
