consolidateStudentData = function(webcat.path, scaled.inc.path, raw.inc.path) {
  if (missing(webcat.path)) {
    webcat.path = 'data/fall-2016/web-cat-students-with-sensordata.csv'
  }
  if (missing(scaled.inc.path)) {
    scaled.inc.path = 'data/fall-2016/scaled_inc.csv'
  }
  if (missing(raw.inc.path)) {
    raw.inc.path = 'data/fall-2016/raw_inc.csv'
  }
  
  webcat.data = read.csv(webcat.path)
  cols.of.interest = c('userName', 'assignment', 'submissionNo', 
           'score.correctness', 'max.score.correctness',
           'elements', 'elementsCovered', 'submissionTimeRaw', 'dueDateRaw')
  webcat.data = webcat.data[, (names(webcat.data) %in% cols.of.interest)]
  webcat.data = webcat.data[order(webcat.data$assignment, webcat.data$userName, -webcat.data$submissionNo), ]
  
  # get the last submission from each user on each project
  last.submissions = webcat.data[!duplicated(data.frame(webcat.data$assignment, webcat.data$userName)), ]
  
  # calculate reftest percentages and discretised project grades
  last.submissions$score.correctness = last.submissions$score.correctness / last.submissions$max.score.correctness
  last.submissions$elementsCovered = last.submissions$elementsCovered / last.submissions$elements
  last.submissions$score.reftest = last.submissions$score.correctness / last.submissions$elementsCovered
  last.submissions$grade.reftest = discretise(last.submissions$score.reftest)
  
  # calculate on-time/late; continuous (in hours) and categorical(true/false)
  submission.times = as.POSIXct(last.submissions$submissionTimeRaw / 1000, origin = '1970-01-01')
  due.times = as.POSIXct(last.submissions$dueDateRaw / 1000, origin = '1970-01-01')
  last.submissions$hours.from.deadline = as.numeric(difftime(due.times, submission.times, units = 'h'))
  last.submissions$on.time.submission = discretise(last.submissions$hours.from.deadline, binom = TRUE)
  
  # read scaled incremental development data and format it
  inc.data = read.csv(scaled.inc.path)
  inc.data = inc.data[, !(names(inc.data) %in% c('ref_test_gains'))] # drop unused metrics
  colnames(inc.data)[1] = 'userName'
  inc.data$userName = gsub('.{7}$', '', inc.data$userName)
  inc.data = inc.data[order(inc.data$assignment, inc.data$userName), ]
  inc.data$composite_inc = (inc.data$early_often + inc.data$checking + inc.data$test_checking + inc.data$test_writing) / 4
  
  # read raw incremental development data and format it
  raw.inc.data = read.csv(raw.inc.path)
  raw.inc.data$test_writing_raw = raw.inc.data$solution_stmt_early_often_raw - raw.inc.data$test_stmt_early_often_raw
  raw.inc.data = raw.inc.data[, !(names(inc.data) %in% c('solution_stmt_early_often_raw', 'test_stmt_early_often_raw'))] # drop unused metrics
  colnames(raw.inc.data)[1] = 'userName'
  raw.inc.data$userName = gsub('.{7}$', '', raw.inc.data$userName)
  raw.inc.data = raw.inc.data[order(raw.inc.data$assignment, raw.inc.data$userName), ]
  
  # merge incremental development scores and project grades
  merged = merge(last.submissions, inc.data, by=c('userName', 'assignment'))
  merged = merge(merged, raw.inc.data, by=c('userName', 'assignment'))
  merged$userName = factor(merged$userName)
  
  # discretise scaled incremental development scores
  merged$grade.early_often = discretise(merged$early_often)
  merged$grade.checking = discretise(merged$checking)
  merged$grade.test_checking = discretise(merged$test_checking)
  merged$grade.test_writing = discretise(merged$test_writing)
  
  return(merged)
}

discretise = function(x, binom = FALSE) {
  if (binom) {
    result = cut(x, c(-Inf, 0, Inf), c('0', '1'), right = TRUE)
  } else {
    result = cut(x, c(-Inf, 0.6, 0.7, 0.8, 0.9, Inf), c('f', 'd', 'c', 'b', 'a'), right = FALSE)
  }
  return(result)
}

webcat.data = consolidateStudentData()