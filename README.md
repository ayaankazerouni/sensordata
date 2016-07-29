# sensordata (Notes for research team)

Data aggregation and visualisation scripts. Sensordata (not included) are required to run these scripts.

### Workflow
1. ```git clone https://github.com/ayaankazerouni/sensordata.git```
2. ```cd sensordata```
3. ```./clean.py <sensordata file> <output file>``` To clean messed up assignment names, add some columns for visualisation, etc.
4. ```./aggregate.sh <output file from previous step>``` This will generate subsessions, worksessions, time spent, and launch stats for each project.

### misc.py
Miscellaneous functions.
* ```./misc.py dist <data file> <column name> [limit]``` gets you all distinct values for a column.
* ```./misc.py sample <data file> <column name> <vals,> <output file>``` Gets you all rows where the given column has one of the given values. Not terribly useful unless you want a small subset of the data (like all events for a student, or a student's project, or Assignment 1) For more complex querying, import the csv file into a SQL client. For MySQL, use the [LOAD DATA INFILE command](http://dev.mysql.com/doc/refman/5.7/en/load-data.html)


### Tentative D3 visualisations

#### Area chart showing programming in a work session:
* ~~Barchart with a student's code-editing activity on a project.~~
* ~~Reflect regular code editing activity as separate from test code editing activity.~~
* Reflect launching activity during programming.
* Reflect regular and test launches as *events* interspersed within editing activity.

Virginia Tech 2016
