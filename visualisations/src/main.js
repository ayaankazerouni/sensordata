import { makeSkylinePlot } from './skylinePlot';
import { makeEventDrops } from './eventDrops';

let body = document.getElementsByTagName('body')[0];
if (body.classList.contains('skyline-plot')) {
  makeSkylinePlot('../../results/ws-14475-p4.csv');
} else if (body.classList.contains('event-drops')) {
  makeEventDrops('../../results/p1-10116-eventDrops.json');
}
