getStudentData = function(webcat.path, inc.path, remove.consistent = FALSE) {
  if (missing(webcat.path)) {
    webcat.path = 'data/fall-2016/web-cat-students-with-sensordata.csv'
  }
  if (missing(inc.path)) {
    inc.path = 'data/fall-2016/scaled_inc.csv'
  }
  webcat.data = read.csv(webcat.path)
  cols.of.interest = c('userName', 'assignment', 'submissionNo', 
           'score.correctness', 'max.score.correctness',
           'elements', 'elementsCovered', 'submissionTimeRaw', 'dueDateRaw')
  webcat.data = webcat.data[, (names(webcat.data) %in% cols.of.interest)]
  webcat.data = webcat.data[order(webcat.data$assignment, webcat.data$userName, -webcat.data$submissionNo), ]
  
  # get the last submission from each user on each project
  last.submissions = webcat.data[!duplicated(data.frame(webcat.data$assignment, webcat.data$userName)), ]
  
  # calculate reftest percentages and discretised grades
  last.submissions$score.correctness = last.submissions$score.correctness / last.submissions$max.score.correctness
  last.submissions$elementsCovered = last.submissions$elementsCovered / last.submissions$elements
  last.submissions$score.reftest = last.submissions$score.correctness / last.submissions$elementsCovered
  last.submissions$grade.reftest = discretise(last.submissions$score.reftest)
  
  # calculate on-time/not-on-time, continuous (in days) and categorical(true/false)
  submission.times = as.POSIXct(last.submissions$submissionTimeRaw / 1000, origin = '1970-01-01')
  due.times = as.POSIXct(last.submissions$dueDateRaw / 1000, origin = '1970-01-01')
  last.submissions$hours.from.deadline = as.numeric(difftime(due.times, submission.times, units = 'h'))
  last.submissions$on.time.submission = discretise(last.submissions$hours.from.deadline, binom = TRUE)
  
  
  # read incremental checking data and format it so it can be matched with grade data
  inc.data = read.csv(inc.path)
  inc.data = inc.data[, !(names(inc.data) %in% c('ref_test_gains'))] # drop unused metrics
  colnames(inc.data)[1] = 'userName'
  inc.data$userName = gsub('.{7}$', '', inc.data$userName) # 
  inc.data = inc.data[order(inc.data$assignment, inc.data$userName), ]
  inc.data$composite_inc = (inc.data$early_often + inc.data$checking + inc.data$test_checking + inc.data$test_writing) / 4
  
  # merge incremental development scores and project grades
  merged = merge(last.submissions, inc.data, by=c('userName', 'assignment'))
  merged$userName = factor(merged$userName)
  
  # discretise scores
  merged$grade.early_often = discretise(merged$early_often)
  merged$grade.checking = discretise(merged$checking)
  merged$grade.test_checking = discretise(merged$test_checking)
  merged$grade.test_writing = discretise(merged$test_writing)

  if (remove.consistent) {
    # remove students who got the same grade on all projects and
    # only keep students who attempted all projects
    merged = merged[!duplicated(merged[c('userName', 'grade.reftest')]), ]
    num.projects = length(levels(merged$assignment))
    username.counts = table(merged$userName)
    keep = names(username.counts[username.counts == num.projects])
    merged = merged[merged$userName %in% keep, ]
  }
  
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

webcat.data = getStudentData()
cols = c('early_often', 'checking', 'test_checking', 'test_writing')

# k-means clustering
set.seed(100)
clust = kmeans(webcat.data[cols], 3)
webcat.data$cluster = factor(clust$cluster)

# PCA for visualisation
pca = prcomp(webcat.data[cols])
pcs = data.frame(PC1 = pca$x[, 1], PC2 = pca$x[, 2], cluster = factor(webcat.data$cluster))
palette(c('red', 'limegreen', 'blue', 'yellow', 'black', 'magenta'))
plot(pcs$PC1, pcs$PC2, pch = 21, bg = pcs$cluster, main = 'PCA-Reduced Data in Clusters',
     xlab = 'PC 1', ylab = 'PC 2', bty = 'L')
legend(x = 'topright', pch=c(21,21,21), pt.bg = levels(pcs$cluster), c('Cluster 1', 'Cluster 2', 'Cluster 3'), bty = '0', cex=0.8)

# contingency table for chi-square analysis
tbl = table(clust$cluster, webcat.data$grade.reftest)
fit.chisq = chisq.test(tbl, simulate.p.value = TRUE)
