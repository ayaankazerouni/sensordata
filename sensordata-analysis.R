# miscellaneous analysis operations
# source('sensordata-utils.R') # before running analyses operations below

# Define some columns of interest for convenience
cols = c( 'test_stmt_early_often_raw', 'solution_stmt_early_often_raw')

# k-means clustering
set.seed(100)
clust = kmeans(webcat.data[cols], 3)
webcat.data$cluster = factor(clust$cluster)

tclust = kmeans(webcat.data$test_stmt_early_often_raw, 2)
webcat.data$tclust = factor(tclust$cluster)

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

# only keep students with at least one A/B score and at least one C/D/F score
# for within subjects analysis
ab = webcat.data[webcat.data$grade.reftest %in% c('a', 'b'), ]
cdf = webcat.data[webcat.data$grade.reftest %in% c('c', 'd', 'f'), ]
intsec = intersect(ab$userId, cdf$userId)
inconsistent = webcat.data[webcat.data$userId %in% intsec, ]