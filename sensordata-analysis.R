# miscellaneous analysis operations
# source('sensordata-utils.R') # before running analyses operations below

# Define some columns of interest for convenience
cols = c( 'earlyOftenIndex', 'testWriting')

# k-means clustering
set.seed(100)
clust = kmeans(webcat.data[cols], 4)
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
  legend(x = 'bottomright', pch=21, pt.bg = levels(pcs$cluster), c('Cluster 1', 'Cluster 2', 'Cluster 3'), bty = '0', cex=0.8)
}

tclust = kmeans(webcat.data$testWriting, 2)
webcat.data$tclust = factor(tclust$cluster)

# contingency table for chi-square analysis
tbl = table(clust$cluster, webcat.data$grade.reftest)
fit.chisq = chisq.test(tbl, simulate.p.value = TRUE)

# only keep students with at least one A/B score and at least one C/D/F score
# for within subjects analysis
webcat.data$ab.cdf = ifelse(webcat.data$grade.reftest %in% c('a', 'b'), 'ab', 'cdf')
ab = webcat.data[webcat.data$grade.reftest %in% c('a', 'b'), ]
cdf = webcat.data[webcat.data$grade.reftest %in% c('c', 'd', 'f'), ]
t1 = webcat.data[webcat.data$tclust == 1, ]
t2 = webcat.data[webcat.data$tclust == 2, ]
intsec = intersect(ab$userId, cdf$userId)
inconsistent = webcat.data[webcat.data$userId %in% intsec, ]

# some subsets for convenience
on.time = webcat.data[webcat.data$on.time.submission == 1, ]
late = webcat.data[webcat.data$on.time.submission == 0, ]
on.time.inconsistent = inconsistent[inconsistent$on.time.submission == 1, ]
late.inconsistent = inconsistent[inconsistent$on.time.submission == 0, ]

# within ss model
# fit = lme(testWriting ~ grade.reftest, random = ~ 1 | userId/grade.reftest, data = test)
# Tukey
# summary(glht(fit,linfct=mcp(grade.reftest = 'Tukey')))