import datetime

def ISO2datetime(s):
	dp, tp = s.split('T')
	y, mo, d = dp.split('-')
	h, mi, s = tp.split(':')
	fs = float(s)
	return datetime.datetime(int(y), int(mo), int(d), int(h), int(mi), int(fs),
				int(1000000*(fs-int(fs)))
				)



def timedelta2float(tdel):
	return 86400.0*tdel.days + tdel.seconds + 1e-6*tdel.microseconds

