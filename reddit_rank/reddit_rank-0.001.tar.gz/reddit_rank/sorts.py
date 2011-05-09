from reddit_rank_sort import hot as _hot, confidence as _confidence

from time import mktime, strptime


TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

def epoch_seconds(timestr):
    return int(mktime(strptime(timestr, TIMESTAMP_FORMAT)))

def hot(ups, downs, timestr):
    return int(_hot(ups+1, downs, epoch_seconds(timestr)) * 100)


SMALLINT = 1 << 16

def confidence(ups, downs):
    return int(_confidence(ups + 1, downs) * SMALLINT)
