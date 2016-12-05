# webcat.data = read.csv('data/fall-2016/web-cat-students-with-sensordata.csv')
webcat.data = webcat.data[, (names(webcat.data) %in% c('userName', 'assignment', 'submissionNo', 
                                                       'score.correctness', 'max.score.correctness'))]
webcat.data = webcat.data[order(webcat.data$assignment, webcat.data$userName, -webcat.data$submissionNo), ]

# get the last submission from each user on each project
last.submissions = webcat.data[!duplicated(data.frame(webcat.data$assignment, webcat.data$userName)), ]
last.submissions$score.correctness = last.submissions$score.correctness / last.submissions$max.score.correctness

discretise.scores = function(submissions, threshold=0.8) {
  if (is.null(threshold) | missing(threshold)) {
    threshold = 0.8
  }
  
  submissions$grade.correctness = ifelse(submissions$score.correctness >= threshold, 'ab', 'cdf')
  return(submissions)
}

last.submissions = discretise.scores(last.submissions)

# read incremental checking data and format it so it can be matched with grade data
inc.data = read.csv('data/fall-2016/scaled_inc.csv')
inc.data = inc.data[, !(names(inc.data) %in% c('ref_test_gains'))] # drop unused metrics
colnames(inc.data)[1] = 'userName'
inc.data$userName = gsub('.{7}$', '', inc.data$userName)
inc.data = inc.data[order(inc.data$assignment, inc.data$userName), ]

# merge incremental development scores and project grades
total = merge(last.submissions, inc.data, by=c('userName', 'assignment'))

# only keep students who attempted all projects
num.projects = length(levels(total$assignment))
username.counts = table(total$userName)
keep = names(username.counts[username.counts == num.projects])
total = total[total$userName %in% keep, ]
