const due_times = require('../due_times.json');

(($, window, document) => {
  const margin = {top: 20, right: 160, bottom: 30, left: 50}; // leaving space for the legend
  const width = 960 - margin.left - margin.right;
  const height = 500 - margin.top - margin.bottom;

  const tickFormat = d3.time.format('%b %d');

  const x = d3.time.scale()
      .range([0, width - 150]);

  const y = d3.scale.linear()
      .range([height, 0]);

  const xAxis = d3.svg.axis()
      .scale(x)
      .ticks(d3.time.day, 3)
      .tickFormat(tickFormat)
      .orient('bottom');

  const yAxis = d3.svg.axis()
      .scale(y)
      .orient('left');

  let editsArea = d3.svg.area()
    .interpolate('basis')
    .x0((d) => x(d.start_time))
    .x1((d) => x(d.end_time))
    .y0(height)
    .y1((d) => y(d.edits));

  let testEditsArea = d3.svg.area()
    .interpolate('basis')
    .x0((d) => x(d.start_time))
    .x1((d) => x(d.end_time))
    .y0(height)
    .y1((d) => y(d.testEdits));

  let launchesArea = d3.svg.area()
    .interpolate('basis')
    .x0((d) => x(d.start_time))
    .x1((d) => x(d.end_time))
    .y0(height)
    .y1((d) => y(d.launches));

  // Line function for due date lines.
  let line = d3.svg.line()
      .x((d) => d.x)
      .y((d) => d.y);

  let svg = d3.select('div.chart-area').append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  d3.csv('ws-2894.csv', (error, data) => {
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
    let start_min = d3.min(data, (d) => d.start_time);
    let end_max = d3.max(data, (d) => d.end_time);
    x.domain([start_min, end_max]);

    let editsMax = d3.max(data, (d) => d.edits);
    let testEditsMax = d3.max(data, (d) => d.testEdits);
    let launchMax = d3.max(data, (d) => d.launches);
    y.domain([0, Math.max(editsMax, testEditsMax, launchMax)]);

    // Draw areas for solution code, test code, and launches. Draw them in order
    // decreasing maximums, so the smallest area ends up in front, and visible.
    let solutionCode = {
      max: editsMax,
      render() {
        svg.append('path')
          .datum(data)
          .attr('data-legend', 'Solution Code')
          .attr('class', 'edits solution-code')
          .attr('d', editsArea);
        }
    };

    let testCode = {
      max: testEditsMax,
      render() {
        svg.append('path')
          .datum(data)
          .attr('data-legend', 'Test Code')
          .attr('class', 'edits test-code')
          .attr('d', testEditsArea);
        }
    };

    let launches = {
      max: launchMax,
      render() {
        svg.append('path')
          .datum(data)
          .attr('data-legend', 'Launches')
          .attr('class', 'launches')
          .attr('d', launchesArea);
        }
    };

    let areas = [ solutionCode, testCode, launches ].sort((a, b) => b.max - a.max);

    for (let i = 0; i < areas.length; i++) {
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
      .attr('transform','translate(' + (width) + ',' + height / 2 + ')')
      .style('font-size', '12px')
      .call(d3.legend);

    // Draw due date lines. Get raw due date info from first row
    // of data. It's the same for all the data in a work_session, anyway.
    let ms1 = +due_times['fall2016']['assignment1']['milestone1'];
    let ms2 = +due_times['fall2016']['assignment1']['milestone2'];
    let ms3 = +due_times['fall2016']['assignment1']['milestone3'];;
    let earlyBonus = +due_times['fall2016']['assignment1']['earlyBonus'];
    let dueTime = +due_times['fall2016']['assignment1']['dueTime'];;

    // Get x-positions scaled by the time scale.
    let dueX = x(new Date(dueTime));
    let ms1X = x(new Date(ms1));
    let ms2X = x(new Date(ms2));
    let ms3X = x(new Date(ms3));
    let earlyX = x(new Date(earlyBonus));

    // Define end-points for each line. Basically top to bottom
    // at the appropriate date on the x-axis.
    let ms1Line = [{ 'x': ms1X, 'y': height }, { 'x': ms1X, 'y': 0 }];
    let ms2Line = [{ 'x': ms2X, 'y': height }, { 'x': ms2X, 'y': 0 }];
    let ms3Line = [{ 'x': ms3X, 'y': height }, { 'x': ms3X, 'y': 0 }];
    let earlyLine = [{ 'x': earlyX, 'y': height }, { 'x': earlyX, 'y': 0 }];
    let dueTimeLine = [{ 'x': dueX, 'y': height }, { 'x': dueX, 'y': 0 }];

    // Draw due date lines.
    let ms1G = svg.append('g')
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

    let ms2G = svg.append('g')
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

    let ms3G = svg.append('g')
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

    let earlyG = svg.append('g')
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

    let dueG = svg.append('g')
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
