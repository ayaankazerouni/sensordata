import eventDrops from 'event-drops';
import moment from 'moment';

export function makeEventDrops(dataFile) {
  d3.json(dataFile, (error, data) => {
    if (error) throw error;

    const start = moment("2016-08-15");
    const end = moment("2016-09-11");

    const config = {
      start,
      end,
      locale: "%S"
    };

    const eventDropsChart = d3.chart.eventDrops(config);
    d3.select('.chart-area')
        .datum(data)
        .call(eventDropsChart);
  });
};
