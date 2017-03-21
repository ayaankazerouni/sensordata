# Miscellaneous analysis operations, in no specific order.
# source(sensordata-utils.R) before using these

# Define some columns of interest for convenience in clustering
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

# 5-fold cross validation
folds = cut(seq(1, nrow(webcat.data)), breaks = 5, labels = FALSE)
accuracy.total = 0

for (i in 1:5) {
  # 0.8/0.2 train/test
  test.indices = which(folds == i, arr.ind = TRUE)
  data.test = webcat.data[test.indices, ]
  data.train = webcat.data[-test.indices, ]
  
  # logistic regression on.time.submission ~ early_often + checking + test_checking + test_writing
  logistic.null = glm(on.time.submission ~ 1, data = data.train, family = binomial(link='logit'))
  logistic.full = glm(on.time.submission ~ early_often + checking + test_checking + test_writing, 
                      family = binomial(link='logit'), data = data.train)
  logistic.final = step(logistic.full, scope = list(upper=logistic.full, lower=logistic.null), direction='backward')
  
  # on-time/not-on-time predictions
  predictions = predict(logistic.final, newdata = data.test)
  predictions = ifelse(predictions > 0.5, 1, 0)
  error = mean(predictions != data.test$on.time.submission)
  accuracy = 1 - error
  accuracy.total = accuracy.total + accuracy
}

accuracy.average = accuracy.total / 5