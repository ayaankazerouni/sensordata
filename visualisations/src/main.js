import { SKYLINE_PLOT, chartToShow } from './chartSelector';
import { makeSkylinePlot } from './skylinePlot';

const chart = chartToShow();
if (chart == SKYLINE_PLOT) {
  makeSkylinePlot('../../results/ws-14475-p4.csv');
}
