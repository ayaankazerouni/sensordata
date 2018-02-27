composite_inc = read.csv("~/Desktop/composite_inc.csv")   # modify path as needed

dir.create("~/Desktop/figures", recursive = TRUE)

# histograms

# score.reftest
setEPS()
postscript('~/Desktop/figures/score-reftest-histogram.eps')
hist(composite_inc$score.reftest * 100, col='cornflowerblue', xlab='Project Score', main='')
dev.off()

# byteEarlyOftenIndex
setEPS()
postscript('~/Desktop/figures/early-often-histogram.eps')
hist(composite_inc$byteEarlyOftenIndex * 100, col='cornflowerblue', xlab='Early/Often Index', main='')
dev.off()

# byteTestWriting
setEPS()
postscript('~/Desktop/figures/test-writing-histogram.eps')
hist(composite_inc$byteTestWriting * 100, col='cornflowerblue', xlab='Incremental Test Writing', main='', breaks=20)
dev.off()

# byteTestChecking
setEPS()
postscript('~/Desktop/figures/test-checking-histogram.eps')
hist(composite_inc$byteTestChecking * 100, col='cornflowerblue', xlab='Incremental Test Checking', main='', breaks=20)
dev.off()

# boxplots
ymin = -4
ymax = 20

# solved ~ byteEarlyOftenIndex
setEPS()
postscript('~/Desktop/figures/early-often-by-solved.eps')
boxplot(composite_inc$byteEarlyOftenIndex, composite_inc$solved, outline=F, names = c('> 95%', '<= 95%'),
        col='cornflowerblue', pch=21, bg='cornflowerblue', ylab='Early/Often Index', xlab='Project Scores',
        ylim=c(ymin, ymax))
dev.off()

# solved ~ solutionByteEarlyOftenIndex
setEPS()
postscript('~/Desktop/figures/solution-early-often-by-solved.eps')
boxplot(composite_inc$solutionByteEarlyOftenIndex, composite_inc$solved, outline=F, names = c('> 95%', '<= 95%'),
        col='cornflowerblue', pch=21, bg='cornflowerblue', ylab='Early/Often Index - Solution Code', xlab='Project Scores',
        ylim=c(ymin, ymax))
dev.off()

# solved ~ testByteEarlyOftenIndex
setEPS()
postscript('~/Desktop/figures/test-early-often-by-solved.eps')
boxplot(composite_inc$testByteEarlyOftenIndex, composite_inc$solved, outline=F, names = c('> 95%', '<= 95%'),
        col='cornflowerblue', pch=21, bg='cornflowerblue', ylab='Early/Often Index - Test Code', xlab='Project Scores',
        ylim=c(ymin, ymax))
dev.off()

# solved ~ testLaunchEarlyOften
setEPS()
postscript('~/Desktop/figures/test-launch-early-often-by-solved.eps')
boxplot(composite_inc$testLaunchEarlyOften, composite_inc$solved, outline=F, names = c('> 95%', '<= 95%'),
        col='cornflowerblue', pch=21, bg='cornflowerblue', ylab='Early/Often Index - Test Launches', xlab='Project Scores',
        ylim=c(ymin, ymax))
dev.off()

# on.time.submission ~ byteEarlyOftenIndex
setEPS()
postscript('~/Desktop/figures/early-often-by-on-time-status.eps')
boxplot(composite_inc$byteEarlyOftenIndex, composite_inc$on.time.submission, outline=F,
        col='cornflowerblue', pch=21, bg='cornflowerblue', ylab='Early/Often Index', names=c('On Time', 'Late'),
        ylim=c(ymin, ymax))
dev.off()

# on.time.submisison ~ solutionByteEarlyOftenIndex
setEPS()
postscript('~/Desktop/figures/solution-early-often-by-on-time-status.eps')
boxplot(composite_inc$solutionByteEarlyOftenIndex, composite_inc$on.time.submission, outline=F,
        col='cornflowerblue', pch=21, bg='cornflowerblue', ylab='Early/Often Index - Solution Code', names=c('On Time', 'Late'),
        ylim=c(ymin, ymax))
dev.off()

# on.time.submission ~ testByteEarlyOftenIndex
setEPS()
postscript('~/Desktop/figures/test-early-often-by-on-time-status.eps')
boxplot(composite_inc$testByteEarlyOftenIndex, composite_inc$on.time.submission, outline=F,
        col='cornflowerblue', pch=21, bg='cornflowerblue', ylab='Early/Often Index - Test Code', names=c('On Time', 'Late'),
        ylim=c(ymin, ymax))
dev.off()

# on.time.submission ~ testLaunchEarlyOften
setEPS()
postscript('~/Desktop/figures/test-launch-early-often-by-on-time-status.eps')
boxplot(composite_inc$testLaunchEarlyOften, composite_inc$on.time.submission, outline=F,
        col='cornflowerblue', pch=21, bg='cornflowerblue', ylab='Early/Often Index - Test Launches', names=c('On Time', 'Late'),
        ylim=c(ymin, ymax))
dev.off()

# scatter plots

# finished.hours.from.deadline ~ byteEarlyOftenIndex
setEPS()
postscript('~/Desktop/figures/early-often-finishing-time-scatter.eps')
plot(composite_inc$byteEarlyOftenIndex, composite_inc$finished.hours.from.deadline, xlab='Early/Often Index',
     ylab='Finishing Time (hours from deadline)', pch=21, bg='cornflowerblue')
abline(lm(finished.hours.from.deadline ~ byteEarlyOftenIndex, data = composite_inc), col='red')
dev.off()

# finished.hours.from.deadline ~ solutionByteEarlyOftenIndex
setEPS()
postscript('~/Desktop/figures/solution-early-often-finishing-time-scatter.eps')
plot(composite_inc$solutionByteEarlyOftenIndex, composite_inc$finished.hours.from.deadline, xlab='Early/Often Index - Solution Code',
     ylab='Finishing Time (hours from deadline)', pch=21, bg='cornflowerblue')
abline(lm(finished.hours.from.deadline ~ solutionByteEarlyOftenIndex, data = composite_inc), col='red')
dev.off()

# finished.hours.from.deadline ~ testByteEarlyOftenIndex
setEPS()
postscript('~/Desktop/figures/test-early-often-finishing-time-scatter.eps')
plot(composite_inc$testByteEarlyOftenIndex, composite_inc$finished.hours.from.deadline, xlab='Early/Often Index - Test Code',
     ylab='Finishing Time (hours from deadline)', pch=21, bg='cornflowerblue')
abline(lm(finished.hours.from.deadline ~ testByteEarlyOftenIndex, data = composite_inc), col='red')
dev.off()

# finished.hours.from.deadline ~ testLaunchEarlyOften
setEPS()
postscript('~/Desktop/figures/test-launch-early-often-finishing-time-scatter.eps')
plot(composite_inc$testLaunchEarlyOften, composite_inc$finished.hours.from.deadline, xlab='Early/Often Index - Test Launches',
     ylab='Finishing Time (hours from deadline)', pch=21, bg='cornflowerblue')
abline(lm(finished.hours.from.deadline ~ testLaunchEarlyOften, data = composite_inc), col='red')
dev.off()

# functions
drawTestSolutionBarplot = function(testCode, solutionCode, pos.legend='top') {
  stopifnot(length(testCode) == length(solutionCode))
  
  m = matrix(data=c(testCode, solutionCode), nrow=2, byrow=T)
  barplot(m, col=c('maroon', 'orange'), beside=T, space=c(0,1), xlab='Work Session #', ylab='Lines changed',
          legend.text=c('Test Code', 'Solution Code'), args.legend=list(x=pos.legend, cex=0.7),
          names.arg=c(1:length(testCode)), cex.names=0.75, ylim=c(0, 1700), yaxt='n')
  ticks = c(0, 500, 1000, 1500, 1700)
  axis(2, at=ticks, labels = ticks)
}