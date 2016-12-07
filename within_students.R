getAggregateData = function(webcat.path, inc.path) {
  webcat.data = read.csv('data/fall-2016/web-cat-students-with-sensordata.csv')
  webcat.data = webcat.data[, (names(webcat.data) %in% c('userName', 'assignment', 'submissionNo', 
                                                         'score.correctness', 'max.score.correctness',
                                                         'elements', 'elementsCovered'))]
  webcat.data = webcat.data[order(webcat.data$assignment, webcat.data$userName, -webcat.data$submissionNo), ]
  
  # get the last submission from each user on each project
  last.submissions = webcat.data[!duplicated(data.frame(webcat.data$assignment, webcat.data$userName)), ]
  last.submissions$score.correctness = last.submissions$score.correctness / last.submissions$max.score.correctness
  last.submissions$elementsCovered = last.submissions$elementsCovered / last.submissions$elements
  last.submissions$score.reftest = last.submissions$score.correctness / last.submissions$elementsCovered
  
  # read incremental checking data and format it so it can be matched with grade data
  inc.data = read.csv('data/fall-2016/scaled_inc.csv')
  inc.data = inc.data[, !(names(inc.data) %in% c('ref_test_gains'))] # drop unused metrics
  colnames(inc.data)[1] = 'userName'
  inc.data$userName = gsub('.{7}$', '', inc.data$userName)
  inc.data = inc.data[order(inc.data$assignment, inc.data$userName), ]
  
  # merge incremental development scores and project grades
  total = merge(last.submissions, inc.data, by=c('userName', 'assignment'))
  total$userName = factor(total$userName)
  
  # only keep students who attempted all projects
  num.projects = length(levels(total$assignment))
  username.counts = table(total$userName)
  keep = names(username.counts[username.counts == num.projects])
  total = total[total$userName %in% keep, ]
  
  # discretise reftest scores to an A-F scale
  grades = cut(total$score.reftest, c(-Inf, 0.6, 0.7, 0.8, 0.9, Inf), c('f', 'd', 'c', 'b', 'a'), right =FALSE)
  total$grade.reftest = grades
  return(total)
}

withinSubjectsAnova = function(data, formula=score.reftest ~ early_often * checking * test_checking * test_writing
                               + Error(userName / (early_often * test_checking))) {
  aov.out = aov(formula, data = data)
  return(aov.out)
}