consolidateStudentData = function(webcat.path, scaled.inc.path,
                                  raw.inc.path, time.path, ref.test.gains.path,
                                  ws.path) {
  if (missing(webcat.path)) {
    webcat.path = 'data/fall-2016/web-cat-students-with-sensordata.csv'
  }
  if (missing(scaled.inc.path)) {
    scaled.inc.path = 'data/fall-2016/scaled_inc_new.csv'
  }
  if (missing(raw.inc.path)) {
    raw.inc.path = 'data/fall-2016/raw_inc.csv'
  }
  if (missing(time.path)) {
    time.path = 'data/fall-2016/time_spent.csv'
  }
  if (missing(ref.test.gains.path)) {
    ref.test.gains.path = 'data/fall-2016/ref_test_gains.csv'
  }
  if (missing(ws.path)) {
    ws.path = 'data/fall-2016/work_sessions.csv'
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
  last.submissions$elementsCovered = (last.submissions$elementsCovered / last.submissions$elements) / 0.98
  last.submissions$elementsCovered = ifelse(last.submissions$elementsCovered > 1.0, 1.0, last.submissions$elementsCovered)
  last.submissions$score.reftest = last.submissions$score.correctness / last.submissions$elementsCovered
  last.submissions$grade.reftest = discretise(last.submissions$score.reftest)

  # read web-cat ref-test-gains data and format it
  ref.test.gains = read.csv(ref.test.gains.path)
  ref.test.gains$jitterGain = ref.test.gains$gainCount / (ref.test.gains$gainCount + ref.test.gains$dropCount)
  ref.test.gains = ref.test.gains[, !(names(ref.test.gains) %in% c('submissionCount', 'medianDaysToFinal'))]

  # read scaled incremental development data and format it
  inc.data = read.csv(scaled.inc.path)
  inc.data = inc.data[, !(names(inc.data) %in% c('ref_test_gains'))] # drop unused metrics
  colnames(inc.data)[1] = 'userName'
  inc.data$userName = gsub('.{7}$', '', inc.data$userName)
  inc.data = inc.data[order(inc.data$assignment, inc.data$userName), ]
  inc.data$composite_inc = (inc.data$early_often + inc.data$checking + inc.data$test_checking + inc.data$test_writing) / 4

  # read raw incremental development data and format it
  # each derived metric is calculated once using changes in raw file size, and once using change in statements
  raw.inc.data = read.csv(raw.inc.path)
  raw.inc.data$byteTestWriting = raw.inc.data$solutionByteEarlyOftenIndex - raw.inc.data$testByteEarlyOftenIndex
  raw.inc.data$byteTestChecking = raw.inc.data$solutionByteEarlyOftenIndex - raw.inc.data$testLaunchEarlyOften
  raw.inc.data$byteNormalChecking = raw.inc.data$solutionByteEarlyOftenIndex - raw.inc.data$normalLaunchEarlyOften
  raw.inc.data$byteChecking = raw.inc.data$solutionByteEarlyOftenIndex - raw.inc.data$launchEarlyOften
  raw.inc.data$byteSkew = 3 * (raw.inc.data$byteEarlyOftenIndex - raw.inc.data$byteEditMedian) / raw.inc.data$byteEditSd
  raw.inc.data$stmtTestWriting = raw.inc.data$solutionStmtEarlyOftenIndex - raw.inc.data$testStmtsEarlyOftenIndex
  raw.inc.data$stmtTestChecking = raw.inc.data$solutionStmtEarlyOftenIndex - raw.inc.data$testLaunchEarlyOften
  raw.inc.data$stmtNormalChecking = raw.inc.data$solutionStmtEarlyOftenIndex - raw.inc.data$normalLaunchEarlyOften
  raw.inc.data$stmtChecking = raw.inc.data$solutionStmtEarlyOftenIndex - raw.inc.data$launchEarlyOften
  raw.inc.data$stmtSkew = 3 * (raw.inc.data$stmtEarlyOftenIndex - raw.inc.data$stmtEditMedian) / raw.inc.data$stmtEditSd
  colnames(raw.inc.data)[colnames(raw.inc.data) == 'email'] = 'userName'
  raw.inc.data$userName = gsub('.{7}$', '', raw.inc.data$userName)
  raw.inc.data = raw.inc.data[order(raw.inc.data$assignment, raw.inc.data$userName), ]

  # read hoursOnProject data and format it
  time.data = read.csv(time.path)
  time.data = time.data[, !(names(time.data) %in% c('userId', 'projectId'))]
  colnames(time.data)[1] = 'userName'
  time.data$userName = gsub('.{7}$', '', time.data$userName)
  time.data = time.data[order(time.data$assignment, time.data$userName), ]

  # read work session data for launching data
  require(plyr)
  ws.data = read.csv(ws.path)
  colnames(ws.data)[colnames(ws.data) == 'CASSIGNMENTNAME'] = 'assignment'
  launchtotals = ddply(ws.data, c('userId', 'assignment'), function(x) {
    y = x[c('testLaunches', 'normalLaunches')]
    apply(y, 2, sum)
  })

  # merge incremental development scores and project grades
  merged = merge(last.submissions, ref.test.gains, by=c('userName', 'assignment'))
  merged = merge(merged, inc.data, by=c('userName', 'assignment'))
  merged = merge(merged, raw.inc.data, by=c('userName', 'userId', 'assignment'))
  merged = merge(merged, time.data, by=c('userName', 'assignment'))
  merged = merge(merged, launchtotals, by=c('userId', 'assignment'))
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

# some subsets for convenience
ab = webcat.data[webcat.data$grade.reftest %in% c('a', 'b'), ]
cdf = webcat.data[webcat.data$grade.reftest %in% c('c', 'd', 'f'), ]
on.time = webcat.data[webcat.data$on.time.submission == 1, ]
late = webcat.data[webcat.data$on.time.submission == 0, ]

# only keep students with at least one A/B score and at least one C/D/F score
# for within subjects analysis
intsec = intersect(ab$userId, cdf$userId)
inconsistent = webcat.data[webcat.data$userId %in% intsec, ]
on.time.inconsistent = inconsistent[inconsistent$on.time.submission == 1, ]
late.inconsistent = inconsistent[inconsistent$on.time.submission == 0, ]

# for contrasts
webcat.data$ab.cdf = factor(ifelse(webcat.data$grade.reftest %in% c('a', 'b'), '1', '0'))
testwriting.ab = webcat.data[!is.na(webcat.data$stmtTestWriting) & webcat.data$stmtTestWriting < 1.5, ]
testwriting.cdf = webcat.data[!is.na(webcat.data$stmtTestWriting) & webcat.data$stmtTestWriting>= 1.5, ]

# within ss model
require(nlme)
fit = lme(submissionNo ~ ab.cdf, random = ~ 1 | userId/grade.reftest, 
          data = webcat.data, na.action = na.omit)
anova(fit)
require(multcomp)
tukey = glht(fit,linfct=mcp(ab.cdf = 'Tukey'))
summary(tukey)

# 5-fold validation
df.temp = webcat.data[, c('ab.cdf', 'byteEarlyOftenIndex', 'byteEditMedian', 'byteEditSd', 'byteSkew')]
df.temp = df.temp[complete.cases(df.temp), ]
df.temp = df.temp[!is.infinite(df.temp$byteSkew), ]
df.temp = df.temp[sample(nrow(df.temp)), ]
folds = cut(seq(1, nrow(df.temp)), breaks=5, labels=FALSE)

precision = 0
accuracy = 0
recall = 0

for (i in 1:5) {
  test.indices = which(folds == i, arr.ind = TRUE)
  data.train = df.temp[-test.indices, ]
  data.test = df.temp[test.indices, ]
  
  ea.null = glm(ab.cdf ~ 1, data = df.temp, family = binomial(link='logit'))
  ea.full = glm(ab.cdf ~ ., data = df.temp, family = binomial(link='logit'))
  ea.final = step(ea.full, scope = list(upper = ea.full, lower = ea.null), direction = 'backward')
  
  pred = predict(ea.final, newdata = data.test)
  pred = ifelse(pred > 0.5, 1, 0)
  data.test$pred = pred
  
  tp = nrow(data.test[data.test$pred == 1 & data.test$ab.cdf == 1, ])
  fp = nrow(data.test[data.test$pred == 1 & data.test$ab.cdf == 0, ])
  tn = nrow(data.test[data.test$pred == 0 & data.test$ab.cdf == 0, ])
  fn = nrow(data.test[data.test$pred == 0 & data.test$ab.cdf == 1, ])
  
  precision[i] = tp / (tp + fp)
  recall[i] = tp / (tp + fn)
  accuracy[i] = (tp + tn) / (tp + tn + fp + fn)
}
