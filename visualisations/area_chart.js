(($, window, document) => {
  var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

  var tickFormat = d3.time.format("%m-%d");

  var x = d3.time.scale()
      .range([0, width]);

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

  var area = d3.svg.area()
      .interpolate('basis')
      .x((d) => x(d.start_time))
      .y0(height)
      .y1((d) => y(d.edits));

  var svg = d3.select("body").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  d3.csv("ws_1316.csv", function(error, data) {
    if (error) throw error;

    var ms1 = -1,
        ms2 = -1,
        ms3 = -1,
        earlyBonus = -1,
        dueTime = -1;

    data.forEach((d) => {
      d.start_time = new Date(+d.start_time);
      d.edits = +d.editSizeStmts + +d.testEditSizeStmts;
      if (ms1 === -1) {
        ms1 = +d.milestone1;
      }

      if (ms2 === -1) {
        ms2 = +d.milestone2;
      }

      if (ms3 === -1) {
        ms3 = +d.milestone3;
      }

      if (earlyBonus === -1) {
        earlyBonus = +d.earlyBonus;
      }

      if (dueTime === -1) {
        dueTime = +d.dueTime;
      }
    });

    x.domain(d3.extent(data, (d) => d.start_time));  // extent finds the min and max in an array. Useful for dates.
    y.domain([0, d3.max(data, (d) => d.edits)]); // using 0 as the min here because we know it already.

    svg.append("path")
        .datum(data)
        .attr("class", "area")
        .attr("d", area);

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
        .text("Edit size in statements");

    var dueX = x(new Date(dueTime));
    var ms1X = x(new Date(ms1));
    var ms2X = x(new Date(ms2));
    var ms3X = x(new Date(ms3));
    var earlyX = x(new Date(earlyBonus));

    ms1Line = [{ "x": ms1X, "y": height }, { "x": ms1X, "y": 0 }];
    ms2Line = [{ "x": ms2X, "y": height }, { "x": ms2X, "y": 0 }];
    ms3Line = [{ "x": ms3X, "y": height }, { "x": ms3X, "y": 0 }];
    earlyLine = [{ "x": earlyX, "y": height }, { "x": earlyX, "y": 0 }];
    dueTimeLine = [{ "x": dueX, "y": height }, { "x": dueX, "y": 0 }];

    line = d3.svg.line()
        .x((d) => d.x)
        .y((d) => d.y)
        .interpolate('linear');

    svg.append("path")
        .attr('class', 'date-line')
        .attr('stroke', 'green')
        .attr('d', line(ms1Line));
    svg.append("path")
        .attr('class', 'date-line')
        .attr('stroke', 'green')
        .attr('d', line(ms2Line));
    svg.append("path")
        .attr('class', 'date-line')
        .attr('stroke', 'green')
        .attr('d', line(ms3Line));
    svg.append("path")
        .attr('class', 'date-line')
        .attr('stroke', 'orange')
        .attr('d', line(earlyLine));
    svg.append("path")
        .attr('class', 'date-line')
        .attr('stroke', 'red')
        .attr('d', line(dueTimeLine));
  });
})(window.jQuery, window, document);
