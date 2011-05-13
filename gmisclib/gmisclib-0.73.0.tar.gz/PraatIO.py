# -*- coding: utf-8 -*-

"""
This code is a modification of 2011 http://www.ling.upenn.edu/~kgorman/py/TextGrid.py .
Thanks to Kyle Gorman.
"""


class BadFileFormat(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)


class IntervalTier:
    """ represents IntervalTier as a list plus some features: min/max time, 
    size, and tier name """

    def __init__(self, name=None, xmin=0, xmax=0):
        self.name = name
        self.xmin = xmin
        self.xmax = xmax
        self.intervals = []
    
    def __str__(self):
        return '<IntervalTier "%s" with %d points>' % (self.name, self.n)

    def __iter__(self):
        return iter(self.intervals)

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        """ return the (i-1)th interval """
        return self.intervals[i]

    def append_Interval(self, xmin, xmax, mark):
        self.intervals.append((xmin, xmax, mark))

    def write(self, fid):
        fid.write('Object class = "IntervalTier"\n')
	fid.write('"%s"\n' % (self.name if self.name is not None else ''))
        fid.write('xmin = %.5f\n' % self.xmin)
        fid.write('xmax = %.5f\n' % self.xmax)
        fid.write('intervals: size = %d\n' % len(self.intervals))
        for (n, interval) in enumerate(self.intervals):
            fid.write('intervals [%d]:\n' % n)
            fid.write('\txmin = %.5f\n' % interval.xmin)
            fid.write('\txmax = %.5f\n' % interval.xmax)
            fid.write('\ttext = "%s"\n' % interval.mark)

def readInterval(fid):
        tmp = fid.readline()
	if tmp.strip() != '"IntervalTier"':
		raise BadFileFormat, "readInterval, IntervalTier: %s" % tmp
	name = fid.readline().rstrip()
	if not(len(name)>1 and name.startswith('"') and name.endswith('"')):
		raise BadFileFormat, "name quoting: %s" % name
	name = name[1:-1]
	xmin = float(fid.readline().rstrip())
	xmax = float(fid.readline().rstrip())
        n = int(fid.readline().rstrip())
	tmp = IntervalTier(name=name, xmin=xmin, xmax=xmax)
	Quote = "'\""
        for i in xrange(n):
            imin  = float(fid.readline().rstrip())
            imax  = float(fid.readline().rstrip())
            imark = fid.readline().rstrip()
            # I don't really know if I should be de-quoting like this.  It works with
            # Jiahong's aligner, but I don't know about the Praat spec.
            if len(imark) >= 2 and imark[0] in Quote and imark[-1]==imark[0]:
		    imark = imark[1:-1]
            tmp.append_Interval(imin, imax, imark)
	return tmp


# File type = "ooTextFile short"
# "TextGrid"
# 
# 0.0125
# 2818.0125
# <exists>
# 2

def readTextGrids(fp):
	if fp.readline().rstrip() != 'File type = "ooTextFile short"':
		raise BadFileFormat, "File type"
	if fp.readline().rstrip() != '"TextGrid"':
		raise BadFileFormat, "TextGrid"
	fp.readline()
	fp.readline()
	fp.readline()
	fp.readline()
	n = int(fp.readline().rstrip())
	if not (0 < n < 100):
		raise BadFileFormat, "n is wild: %d" % n
	rv = {}
	for i in range(n):
		tmp = readInterval(fp)
		rv[tmp.name] = tmp
	return rv



if __name__ == '__main__':
	import sys
	print readTextGrids(sys.stdin)
