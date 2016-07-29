(($, window, document) => {
  var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

  var tickFormat = d3.time.format("%b %d");

  var x = d3.time.scale()
      .range([0, width - 150]);

  var y = d3.scale.linear()
      .range([height, 0]);

  var xAxis = d3.svg.axis()
      .scale(x)
      .ticks(d3.time.day, 3)
      .tickFormat(tickFormat)
      .orient("bottom");

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left");

  var editsArea = d3.svg.area()
      .interpolate('basis')
      .x((d) => x(d.start_time))
      .y0(height)
      .y1((d) => y(d.edits));

  var testEditsArea = d3.svg.area()
      .interpolate('basis')
      .x((d) => x(d.start_time))
      .y0(height)
      .y1((d) => y(d.testEdits));

  var svg = d3.select("body").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  d3.csv("ws_1012.csv", function(error, data) {
    if (error) throw error;

    // Prepare the data for visualisations. Basically we're making them dates or numbers,
    // depending on how we want to use them.
    data.forEach((d) => {
      d.start_time = new Date(+d.start_time);
      d.edits = +d.editSizeStmts;
      d.testEdits = +d.testEditSizeStmts;
    });

    // Specify input domains for the scales.
    x.domain(d3.extent(data, (d) => d.start_time));  // extent finds the min and max in an array. Useful for dates.
    y.domain([0, d3.max(data, (d) => d.edits)]); // using 0 as the min here because we know it already.

    // Draw the area for regular edits using the editsArea function.
    svg.append("path")
        .datum(data)
        .attr('data-legend', 'Solution Code')
        .attr("class", "edits")
        .attr("d", editsArea);

    // Draw the area for test edits using the testEditsArea function.
    svg.append("path")
        .datum(data)
        .attr('data-legend', 'Test Code')
        .attr("class", "test-edits")
        .attr("d", testEditsArea);

    // Draw axes.
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Statements changed");

    svg.append("g")
      .attr('class', 'legend')
      .attr("transform","translate(" + (width - 140) + ",30)")
      .style('font-size', '12px')
      .call(d3.legend);

    // Draw due date lines. Get raw due date info from first row
    // of data. It's the same for all the data in a work_session, anyway.
    var first = data[0];
    var ms1 = +first.milestone1;
    var ms2 = +first.milestone2;
    var ms3 = +first.milestone3;
    var earlyBonus = +first.earlyBonus;
    var dueTime = +first.dueTime;

    // Get x-positions scaled by the time scale.
    var dueX = x(new Date(dueTime));
    var ms1X = x(new Date(ms1));
    var ms2X = x(new Date(ms2));
    var ms3X = x(new Date(ms3));
    var earlyX = x(new Date(earlyBonus));

    // Define end-points for each line. Basically top to bottom
    // at the appropriate date on the x-axis.
    ms1Line = [{ "x": ms1X, "y": height }, { "x": ms1X, "y": 0 }];
    ms2Line = [{ "x": ms2X, "y": height }, { "x": ms2X, "y": 0 }];
    ms3Line = [{ "x": ms3X, "y": height }, { "x": ms3X, "y": 0 }];
    earlyLine = [{ "x": earlyX, "y": height }, { "x": earlyX, "y": 0 }];
    dueTimeLine = [{ "x": dueX, "y": height }, { "x": dueX, "y": 0 }];

    // Line function for due date lines.
    line = d3.svg.line()
        .x((d) => d.x)
        .y((d) => d.y);

    // Draw due date lines.
    ms1G = svg.append("g")
      .attr("id", "group-ms-1");
    ms1G.append("path")
      .attr('class', 'date-line')
      .attr('stroke', 'green')
      .attr('d', line(ms1Line))
    ms1G.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", ms1X + 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Milestone 1 Due")
      .attr("fill", 'green');

    ms2G = svg.append("g")
      .attr("id", "group-ms-2");
    ms2G.append("path")
      .attr('class', 'date-line')
      .attr('stroke', 'green')
      .attr('d', line(ms2Line));
    ms2G.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", ms2X + 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Milestone 2 Due")
      .attr("fill", 'green');

    ms3G = svg.append("g")
      .attr("id", "group-ms-3");
    ms3G.append("path")
      .attr('class', 'date-line')
      .attr('stroke', 'green')
      .attr('d', line(ms3Line));
    ms3G.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", ms3X + 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Milestone 3 Due")
      .attr("fill", 'green');

    earlyG = svg.append("g")
      .attr("id", "group-early")
    earlyG.append("path")
      .attr('class', 'date-line')
      .attr('stroke', 'orange')
      .attr('d', line(earlyLine));
    ms3G.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", earlyX + 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Early Bonus Deadline")
      .attr("fill", 'orange');

    dueG = svg.append("g")
      .attr("id", "group-due");
    dueG.append("path")
      .attr('class', 'date-line')
      .attr('stroke', 'red')
      .attr('d', line(dueTimeLine));
    dueG.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", dueX + 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Final Submission Due")
      .attr("fill", 'red');
  });
})(window.jQuery, window, document);
