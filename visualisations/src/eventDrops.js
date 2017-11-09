import moment from 'moment';

export function makeEventDrops(dataFile) {
  d3.json(dataFile, (error, data) => {
    if (error) throw error;

    const start = d3.min(data[0].data.concat(data[1].data).concat(data[2].data));
    const end = moment('2016-09-12');

    const config = {
      start,
      end,
      locale: "%S",
      zoomable: false,
      eventLineColor(e) {
        if (e.name.includes('Normal')) {
          return 'maroon';
        } else if (e.name.includes('Test')) {
          return 'orange';
        }
      }
    };

    const eventDropsChart = d3.chart.eventDrops(config);
    d3.select('.chart-area')
        .datum(data)
        .call(eventDropsChart);
  });
};
