# miscellaneous analysis operations
# source('sensordata-utils.R') # before running analyses operations below

# Define some columns of interest for convenience
cols = c('scaled.gainPercent', 'scaled.earlyOftenIndex', 'scaled.testWriting', 'scaled.testLaunchEarlyOften')

# k-means clustering
set.seed(100)
webcat.data$scaled.gainPercent = scale(webcat.data$gainPercent)
webcat.data$scaled.earlyOftenIndex = scale(webcat.data$earlyOftenIndex)
webcat.data$scaled.testWriting = scale(webcat.data$testWriting)
webcat.data$scaled.testLaunchEarlyOften = scale(webcat.data$testLaunchEarlyOften)

# this clustering isn't exciting.
clust = kmeans(webcat.data[cols], 3)
webcat.data$cluster = factor(clust$cluster)

draw.silhoette = function(clust) {
  # silhoette analysis
  library(cluster)
  dissE = daisy(webcat.data[cols])
  sk = silhouette(clust$cluster, dissE)
  palette(c('black', 'darkorange2', 'darkred', 'darkblue'))
  plot(sk, col=1:4, border=NA)
}

plot.pcs = function(cols, cluster.column) {
  # PCA for visualisation
  pca = prcomp(webcat.data[cols])
  pcs = data.frame(PC1 = pca$x[, 1], PC2 = pca$x[, 2], cluster = factor(webcat.data[, cluster.column]))
  palette(c('red', 'limegreen', 'blue', 'yellow', 'darkorange', 'white'))
  plot(pcs$PC1, pcs$PC2, pch = 21, bg = pcs$cluster, main = 'PCA-Reduced Data in Clusters',
       xlab = 'PC 1', ylab = 'PC 2', bty = 'L')
  legend(x = 'bottomright', pch=21, pt.bg = levels(pcs$cluster), c('Cluster 1', 'Cluster 2', 'Cluster 3', 'Cluster 4'), bty = '0', cex=0.8)
}

# contingency table for chi-square analysis
tbl = table(clust$cluster, webcat.data$grade.reftest)
fit.chisq = chisq.test(tbl, simulate.p.value = TRUE)

# only keep students with at least one A/B score and at least one C/D/F score
# for within subjects analysis
ab = webcat.data[webcat.data$grade.reftest %in% c('a', 'b'), ]
cdf = webcat.data[webcat.data$grade.reftest %in% c('c', 'd', 'f'), ]
intsec = intersect(ab$userId, cdf$userId)
inconsistent = webcat.data[webcat.data$userId %in% intsec, ]

# for contrasts
webcat.data$ab.cdf = factor(ifelse(webcat.data$grade.reftest %in% c('a', 'b'), '1', '0'))
testwriting.ab = webcat.data[webcat.data$testWriting < 1.5, ]
testwriting.cdf = webcat.data[webcat.data$testWriting > 1.5, ]

# some subsets for convenience
on.time = webcat.data[webcat.data$on.time.submission == 1, ]
late = webcat.data[webcat.data$on.time.submission == 0, ]
on.time.inconsistent = inconsistent[inconsistent$on.time.submission == 1, ]
late.inconsistent = inconsistent[inconsistent$on.time.submission == 0, ]

# within ss model
# fit = lme(testWriting ~ grade.reftest, random = ~ 1 | userId/grade.reftest, data = test)
# Tukey
# summary(glht(fit,linfct=mcp(grade.reftest = 'Tukey')))
# 

accuracies = 0
precisions = 0
recalls = 0

folds = cut(seq(1, nrow(webcat.data)), breaks=5, labels=FALSE)
for(i in 1:5) {
  test.indices = which(folds == i, arr.ind = TRUE)
  data.test = webcat.data[test.indices, ]
  data.train = webcat.data[-test.indices, ]

  null = glm(ab.cdf ~ 1, family = binomial(link='logit'), data = data.train)
  full = glm(ab.cdf ~ testWriting + earlyOftenIndex + testLaunchEarlyOften,
             family = binomial(link='logit'), data = data.train)
  final = step(full, scope = list(upper=full, lower=null), direction='backward')

  predictions = predict(final, newdata = data.test)
  # predictions = ifelse(predictions > 0, 1, 0)
  predictions = 1
  data.test$prediction = predictions

  tp = nrow(data.test[data.test$ab.cdf == 1 & data.test$prediction == 1, ])
  fp = nrow(data.test[data.test$ab.cdf == 0 & data.test$prediction == 1, ])
  tn = nrow(data.test[data.test$ab.cdf == 0 & data.test$prediction == 0, ])
  fn = nrow(data.test[data.test$ab.cdf == 1 & data.test$prediction == 0, ])


  accuracies[i] = (tp + tn) / (tp + tn + fp + fn)
  precisions[i] = tp / (tp + fp)
  recalls[i] = tp / (tp + fn)
}