$(document).ready(function() {
  var width = 600;
  var height = 300;
  var axisPadding = 30;
  var xPadding = 1;
  var xScale = d3.scale.linear()
    .domain([0, 750])
    .range([0, width - axisPadding]);
  var xAxisScale = d3.scale.linear()
    .domain([0, 750])
    .range([axisPadding, width - axisPadding]);
  var svg = d3.select('#first-chart')
    .append('svg')
      .attr('width', width)
      .attr('height', height);

  // Change the file name below to an existing file.
  d3.csv('./work_sessions124.csv', function(err, dataset) {
    if (err) throw err;

    var widths = [];
    dataset.forEach(function(data) {
      var length = (+data.end_time - +data.start_time) / 60000;
      widths.push(length);
    });

    var yScale = d3.scale.linear()
      .domain([0, d3.max(dataset, function(d) { return parseFloat(d.editsPerLaunch); })])
      .range([height - axisPadding, axisPadding]);
    var yAxisScale = d3.scale.linear()
      .domain([0, height - axisPadding])
      .range([height - axisPadding, axisPadding]);

    var xAxis = d3.svg.axis()
      .scale(xAxisScale)
      .orient('bottom');
    var yAxis = d3.svg.axis()
      .scale(yAxisScale)
      .orient('left');

    svg.selectAll('rect')
      .data(dataset).enter()
      .append('rect')
        .attr('x', function(d, i) {
          var sum = 0;
          for (var index = 0; index < i && index < widths.length; index++) {
            sum += (widths[index] / 4);
          }
          return xScale(sum) + axisPadding;
        })
        .attr('y', function(d) {
          return height - yScale(parseFloat(d.editsPerLaunch)) - axisPadding;
        })
        .attr('width', function(d) {
          var length = (+d.end_time - +d.start_time) / 60000;
          if (xScale(length) > xPadding) {
            return xScale(length / 4) - xPadding;
          } else {
            return xScale(length / 4);
          }
        })
        .attr('height', function(d) {
          return yScale(parseFloat(d.editsPerLaunch));
        })
        .attr('fill', 'maroon');

    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(0, ' + (height - axisPadding) + ')')
      .call(xAxis);
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(' + axisPadding + ', 0)')
      .call(yAxis);
  });

  var svg2 = d3.select('#second-chart')
    .append('svg')
      .attr('width', width)
      .attr('height', height);

  //  Change the file name below to an existing file.
  d3.csv('./work_sessions138.csv', function(err, dataset) {
    if (err) console.error(err);

    var widths = [];
    dataset.forEach(function(data) {
      var length = (+data.end_time - +data.start_time) / 60000;
      widths.push(length);
    });

    var yScale = d3.scale.linear()
      .domain([0, d3.max(dataset, function(d) { return parseFloat(d.editsPerLaunch); })])
      .range([height - axisPadding, axisPadding]);
    var yAxisScale = d3.scale.linear()
      .domain([0, height - axisPadding])
      .range([height - axisPadding, axisPadding]);

    var xAxis = d3.svg.axis()
      .scale(xAxisScale)
      .orient('bottom');
    var yAxis = d3.svg.axis()
      .scale(yAxisScale)
      .orient('left');

    svg2.selectAll('rect')
      .data(dataset).enter()
      .append('rect')
        .attr('x', function(d, i) {
          var sum = 0;
          for (var index = 0; index < i && index < widths.length; index++) {
            sum += (widths[index] / 4);
          }
          return xScale(sum) + axisPadding;
        })
        .attr('y', function(d) {
          return height - yScale(parseFloat(d.editsPerLaunch)) - axisPadding;
        })
        .attr('width', function(d) {
          var length = (+d.end_time - +d.start_time) / 60000;
          if (xScale(length) > xPadding) {
            return xScale(length / 4) - xPadding;
          } else {
            return xScale(length / 4);
          }
        })
        .attr('height', function(d) {
          return yScale(parseFloat(d.editsPerLaunch));
        })
        .attr('fill', 'maroon');

    svg2.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(0, ' + (height - axisPadding) + ')')
      .call(xAxis);
    svg2.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(' + axisPadding + ', 0)')
      .call(yAxis);
  });
});
