consolidateStudentData = function(webcat.path, scaled.inc.path, raw.inc.path, time.path, ref.test.gains.path) {
  if (missing(webcat.path)) {
    webcat.path = 'data/fall-2016/web-cat-students-with-sensordata.csv'
  }
  if (missing(scaled.inc.path)) {
    scaled.inc.path = 'data/fall-2016/scaled_inc_new.csv'
  }
  if (missing(raw.inc.path)) {
    raw.inc.path = 'data/fall-2016/raw_inc_copy.csv'
  }
  if (missing(time.path)) {
    time.path = 'data/fall-2016/time_spent.csv'
  }
  if (missing(ref.test.gains.path)) {
    ref.test.gains.path = 'data/fall-2016/ref_test_gains.csv'
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
  
  # read web-cat ref-test-gains data and format it
  ref.test.gains = read.csv(ref.test.gains.path)
  ref.test.gains$jitterGain = ref.test.gains$gainCount / (ref.test.gains$gainCount + ref.test.gains$dropCount)
  ref.test.gains = ref.test.gains[, !(names(ref.test.gains) %in% c('submissionCount', 'medianDaysToFinal'))]
  
  # read scaled incremental development data and format it
  inc.data = read.csv(scaled.inc.path)
  # inc.data = inc.data[, !(names(inc.data) %in% c('ref_test_gains'))] # drop unused metrics
  colnames(inc.data)[1] = 'userName'
  inc.data$userName = gsub('.{7}$', '', inc.data$userName)
  inc.data = inc.data[order(inc.data$assignment, inc.data$userName), ]
  inc.data$composite_inc = (inc.data$early_often + inc.data$checking + inc.data$test_checking + inc.data$test_writing) / 4
  
  # read raw incremental development data and format it
  raw.inc.data = read.csv(raw.inc.path)
  raw.inc.data$testWriting = raw.inc.data$solutionStmtEarlyOftenIndex - raw.inc.data$testStmtsEarlyOftenIndex
  raw.inc.data$testCheckingRaw = raw.inc.data$solutionStmtEarlyOftenIndex - raw.inc.data$testLaunchEarlyOften
  raw.inc.data$solutionCheckingRaw = raw.inc.data$solutionStmtEarlyOftenIndex - raw.inc.data$normalLaunchEarlyOften
  raw.inc.data$checkingRaw = raw.inc.data$solutionStmtEarlyOftenIndex - raw.inc.data$launchEarlyOften
  colnames(raw.inc.data)[1] = 'userName'
  raw.inc.data$userName = gsub('.{7}$', '', raw.inc.data$userName)
  raw.inc.data = raw.inc.data[order(raw.inc.data$assignment, raw.inc.data$userName), ]
  
  # read hoursOnProject data and format it
  time.data = read.csv(time.path)
  time.data = time.data[, !(names(time.data) %in% c('userId', 'projectId'))]
  colnames(time.data)[1] = 'userName'
  time.data$userName = gsub('.{7}$', '', time.data$userName)
  time.data = time.data[order(time.data$assignment, time.data$userName), ]
  
  # merge incremental development scores and project grades
  merged = merge(last.submissions, ref.test.gains, by=c('userName', 'assignment'))
  merged = merge(merged, inc.data, by=c('userName', 'assignment'))
  merged = merge(merged, raw.inc.data, by=c('userName', 'userId', 'assignment'))
  merged = merge(merged, time.data, by=c('userName', 'assignment'))
  merged$userName = factor(merged$userName)
  
  # calculate on-time/late; continuous (in hours) and categorical(true/false)
  submission.times = as.POSIXct(merged$submissionTimeRaw / 1000, origin = '1970-01-01')
  due.times = as.POSIXct(merged$dueDateRaw / 1000, origin = '1970-01-01')
  start.times = as.POSIXct(merged$projectStartTime / 1000, origin = '1970-01-01')
  merged$finished.hours.from.deadline = as.numeric(difftime(due.times, submission.times, units = 'h'))
  merged$started.days.from.deadline = as.numeric(difftime(due.times, start.times, units = 'd'))
  merged$on.time.submission = discretise(merged$finished.hours.from.deadline, binom = TRUE)
  merged$userId = factor(merged$userId)
  
  # discretise scaled incremental development scores
  merged$grade.early_often = discretise(merged$early_often)
  merged$grade.checking = discretise(merged$checking)
  merged$grade.test_checking = discretise(merged$test_checking)
  merged$grade.test_writing = discretise(merged$test_writing)
  
  merged = merged[merged$hoursOnProject >= 1, ]
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
