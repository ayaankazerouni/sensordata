export const SKYLINE_PLOT = 'skylinePlot'
export function chartToShow() {
  let body = document.getElementsByTagName('body')[0];
  if (body.classList.contains('skyline-plot')) {
    return SKYLINE_PLOT;
  }
}
