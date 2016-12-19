getStudentData = function(webcat.path, inc.path, remove.consistent = FALSE) {
  if (missing(webcat.path)) {
    webcat.path = 'data/fall-2016/web-cat-students-with-sensordata.csv'
  }
  if (missing(inc.path)) {
    inc.path = 'data/fall-2016/scaled_inc.csv'
  }
  webcat.data = read.csv(webcat.path)
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
  inc.data = read.csv(inc.path)
  inc.data = inc.data[, !(names(inc.data) %in% c('ref_test_gains'))] # drop unused metrics
  colnames(inc.data)[1] = 'userName'
  inc.data$userName = gsub('.{7}$', '', inc.data$userName)
  inc.data = inc.data[order(inc.data$assignment, inc.data$userName), ]
  inc.data$total_grade = (inc.data$early_often + inc.data$checking + inc.data$test_checking + inc.data$test_writing) / 4
  
  # merge incremental development scores and project grades
  total = merge(last.submissions, inc.data, by=c('userName', 'assignment'))
  total$userName = factor(total$userName)
  
  # discretise scores
  total$grade.reftest = discretise(total$score.reftest)
  total$grade.early_often = discretise(total$early_often)
  total$grade.checking = discretise(total$checking)
  total$grade.test_checking = discretise(total$test_checking)
  total$grade.test_writing = discretise(total$test_writing)

  if (remove.consistent) {
    # remove students who got the same grade on all projects and
    # only keep students who attempted all projects
    total = total[!duplicated(total[c('userName', 'grade.reftest')]), ]
    num.projects = length(levels(total$assignment))
    username.counts = table(total$userName)
    keep = names(username.counts[username.counts == num.projects])
    total = total[total$userName %in% keep, ]
  }
  
  return(total)
}

discretise = function(x) {
  result = cut(x, c(-Inf, 0.6, 0.7, 0.8, 0.9, Inf), c('f', 'd', 'c', 'b', 'a'), right = FALSE)
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
pcs = data.frame(PC1 = pca$x[, 1], PC2 = pca$x[, 2], cluster = factor(clust$cluster))
palette(c('red', 'limegreen', 'blue', 'yellow', 'black', 'magenta'))
plot(pcs$PC1, pcs$PC2, pch = 21, bg = pcs$cluster, main = 'PCA-Reduced Data in Clusters',
     xlab = 'PC 1', ylab = 'PC 2', bty = 'L')
legend(x = 'topright', pch=c(21,21,21), pt.bg = levels(pcs$cluster), c('Cluster 1', 'Cluster 2', 'Cluster 3'), bty = '0', cex=0.8)

# contingency table for chi-square analysis
tbl = table(clust$cluster, webcat.data$grade.reftest)

# ANOVA grade ~ cluster
fit = aov(score.reftest ~ cluster, data = webcat.data)