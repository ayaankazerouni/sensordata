# miscellaneous analysis operations
# source('sensordata-utils.R') # before running analyses operations below

# only keep students with at least one A/B score and at least one C/D/F score
# for within subjects analysis
ab = webcat.data[webcat.data$grade.reftest %in% c('a', 'b'), ]
cdf = webcat.data[webcat.data$grade.reftest %in% c('c', 'd', 'f'), ]
intsec = intersect(ab$userId, cdf$userId)
inconsistent = webcat.data[webcat.data$userId %in% intsec, ]

# for contrasts
webcat.data$ab.cdf = factor(ifelse(webcat.data$grade.reftest %in% c('a', 'b'), '1', '0'))
testwriting.ab = webcat.data[!is.na(webcat.data$testWriting) & webcat.data$testWriting < 1.5, ]
testwriting.cdf = webcat.data[!is.na(webcat.data$testWriting) & webcat.data$testWriting >= 1.5, ]

# some subsets for convenience
on.time = webcat.data[webcat.data$on.time.submission == 1, ]
late = webcat.data[webcat.data$on.time.submission == 0, ]
on.time.inconsistent = inconsistent[inconsistent$on.time.submission == 1, ]
late.inconsistent = inconsistent[inconsistent$on.time.submission == 0, ]

# within ss model
# fit = lme(testWriting ~ grade.reftest, random = ~ 1 | userId/grade.reftest, data = test)
# Tukey
# summary(glht(fit,linfct=mcp(grade.reftest = 'Tukey')))
