(($, window, document) => {
  var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

  var tickFormat = d3.time.format('%b %d');

  var x = d3.time.scale()
      .range([0, width - 150]);

  var y = d3.scale.linear()
      .range([height, 0]);

  var xAxis = d3.svg.axis()
      .scale(x)
      .ticks(d3.time.day, 3)
      .tickFormat(tickFormat)
      .orient('bottom');

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient('left');

  var editsArea = d3.svg.area()
    .interpolate('step')
    .x0((d) => x(d.start_time))
    .x1((d) => x(d.end_time))
    .y0(height)
    .y1((d) => y(d.edits));

  var testEditsArea = d3.svg.area()
    .interpolate('step')
    .x0((d) => x(d.start_time))
    .x1((d) => x(d.end_time))
    .y0(height)
    .y1((d) => y(d.testEdits));

  var launchesArea = d3.svg.area()
    .interpolate('step')
    .x0((d) => x(d.start_time))
    .x1((d) => x(d.end_time))
    .y0(height)
    .y1((d) => y(d.launches));

  // Line function for due date lines.
  var line = d3.svg.line()
      .x((d) => d.x)
      .y((d) => d.y);

  var svg = d3.select('div.chart-area').append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  d3.csv('ws_135.csv', function(error, data) {
    if (error) throw error;

    // Prepare the data for visualisations. Basically we're making them dates or numbers,
    // depending on how we want to use them.
    data.forEach((d) => {
      d.start_time = new Date(+d.start_time);
      d.end_time = new Date(+d.end_time);
      d.edits = +d.editSizeStmts;
      d.testEdits = +d.testEditSizeStmts;
      d.launches = +d.testLaunches + +d.normalLaunches;
    });

    // Specify input domains for the scales.
    var start_min = d3.min(data, (d) => d.start_time);
    var end_max = d3.max(data, (d) => d.end_time);
    x.domain([start_min, end_max]);

    var editsMax = d3.max(data, (d) => d.edits);
    var testEditsMax = d3.max(data, (d) => d.testEdits);
    var launchMax = d3.max(data, (d) => d.launches);
    y.domain([0, Math.max(editsMax, testEditsMax, launchMax)]);

    // Draw areas for solution code, test code, and launches. Draw them in order
    // decreasing maximums, so the smallest area ends up in front, and visible.
    var solutionCode = {
      max: editsMax,
      render: function() {
        svg.append('path')
          .datum(data)
          .attr('data-legend', 'Solution Code')
          .attr('class', 'edits solution-code')
          .attr('d', editsArea);
        }
    };

    var testCode = {
      max: testEditsMax,
      render: function() {
        svg.append('path')
          .datum(data)
          .attr('data-legend', 'Test Code')
          .attr('class', 'edits test-code')
          .attr('d', testEditsArea);
        }
    };

    var launches = {
      max: launchMax,
      render: function() {
        svg.append('path')
          .datum(data)
          .attr('data-legend', 'Launches')
          .attr('class', 'launches')
          .attr('d', launchesArea);
        }
    };

    var areas = [ solutionCode, testCode, launches ].sort((a, b) => b.max - a.max);

    for (var i = 0; i < areas.length; i++) {
      areas[i].render();
    }

    // Draw axes.
    svg.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis);

    svg.append('g')
        .attr('class', 'y axis')
        .call(yAxis)
      .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr('dy', '.71em')
        .style('text-anchor', 'end')
        .text('Statements changed / Launch count');

    // Draw legend
    svg.append('g')
      .attr('class', 'legend')
      .attr('transform','translate(' + (width - 140) + ',' + height / 2 + ')')
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
    var ms1Line = [{ 'x': ms1X, 'y': height }, { 'x': ms1X, 'y': 0 }];
    var ms2Line = [{ 'x': ms2X, 'y': height }, { 'x': ms2X, 'y': 0 }];
    var ms3Line = [{ 'x': ms3X, 'y': height }, { 'x': ms3X, 'y': 0 }];
    var earlyLine = [{ 'x': earlyX, 'y': height }, { 'x': earlyX, 'y': 0 }];
    var dueTimeLine = [{ 'x': dueX, 'y': height }, { 'x': dueX, 'y': 0 }];

    // Draw due date lines.
    var ms1G = svg.append('g')
      .attr('id', 'group-ms-1');
    ms1G.append('path')
      .attr('class', 'date-line milestone')
      .attr('d', line(ms1Line))
    ms1G.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', ms1X + 6)
      .attr('dy', '.71em')
      .style('text-anchor', 'end')
      .text('Milestone 1 Due')
      .attr('fill', '#336699');

    var ms2G = svg.append('g')
      .attr('id', 'group-ms-2');
    ms2G.append('path')
      .attr('class', 'date-line milestone')
      .attr('d', line(ms2Line));
    ms2G.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', ms2X + 6)
      .attr('dy', '.71em')
      .style('text-anchor', 'end')
      .text('Milestone 2 Due')
      .attr('fill', '#336699');

    var ms3G = svg.append('g')
      .attr('id', 'group-ms-3');
    ms3G.append('path')
      .attr('class', 'date-line milestone')
      .attr('d', line(ms3Line));
    ms3G.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', ms3X + 6)
      .attr('dy', '.71em')
      .style('text-anchor', 'end')
      .text('Milestone 3 Due')
      .attr('fill', '#336699');

    var earlyG = svg.append('g')
      .attr('id', 'group-early')
    earlyG.append('path')
      .attr('class', 'date-line early')
      .attr('d', line(earlyLine));
    earlyG.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', earlyX + 6)
      .attr('dy', '.71em')
      .style('text-anchor', 'end')
      .text('Early Bonus Deadline')
      .attr('fill', '#cc6600');

    var dueG = svg.append('g')
      .attr('id', 'group-due');
    dueG.append('path')
      .attr('class', 'date-line due')
      .attr('d', line(dueTimeLine));
    dueG.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', dueX + 6)
      .attr('dy', '.71em')
      .style('text-anchor', 'end')
      .text('Final Submission Due')
      .attr('fill', 'red');
  });
})(window.jQuery, window, document);
