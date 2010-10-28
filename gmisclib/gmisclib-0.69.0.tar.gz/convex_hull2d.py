#!/usr/bin/env python

"""convexhull.py

Calculate the convex hull of a set of n 2D-points in O(n log n) time.  
Taken from Berg et al., Computational Geometry, Springer-Verlag, 1997.
Prints output as EPS file.

When run from the command line it generates a random set of points
inside a square of given length and finds the convex hull for those,
printing the result as an EPS file.

Usage: convexhull.py <numPoints> <squareLength> <outFile>

Dinu C. Gherman

Small Bug: Only works with a list of UNIQUE points, Evan Jones, 2005/05/18
If the list of points passed to this function is not unique, it will raise an assertion.
To fix this, remove these lines from the beginning of the convexHull function:

Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66527
and modified to work with complex numbers.

"""


import sys, random

class DuplicatePoints(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)


######################################################################
# Helpers
######################################################################

def _myDet(p, q, r):
    """Calc. determinant of a special matrix with three 2D points.

    The sign, "-" or "+", determines the side, right or left,
    respectivly, on which the point r lies, when measured against
    a directed vector from p to q.
    """

    # We use Sarrus' Rule to calculate the determinant.
    # (could also use the Numeric package...)
    # sum1 = q[0]*r[1] + p[0]*q[1] + r[0]*p[1]
    # sum1 = q.real*r.imag + p.real*q.imag + r.real*p.imag
    # sum2 = q[0]*p[1] + r[0]*q[1] + p[0]*r[1]
    # sum2 = q.real*p.imag + r.real*q.imag + p.real*r.imag
    sum = q.real*(r.imag-p.imag) + p.real*(q.imag-r.imag) + r.real*(p.imag-q.imag)

    # return sum1 - sum2
    return sum


def _isRightTurn((p, q, r)):
    "Do the vectors pq:qr form a right turn, or not?"
    if p==q or p==r or q==r:
	if p==q:
		dup = p
	elif p==r:
		dup = p
	elif q==r:
		dup = q
    	raise DuplicatePoints, 'Two points are identical at %s' % str(dup)
    return _myDet(p, q, r) < 0


def _isPointInPolygon(r, P):
    "Is point r inside a given polygon P?"

    # We assume the polygon is a list of points, listed clockwise!
    for i in xrange(len(P[:-1])):
        p, q = P[i], P[i+1]
        if not _isRightTurn((p, q, r)):
            return False # Out!        

    return True # It's within!


def _makeRandomData(numPoints=30, sqrLength=100, addCornerPoints=0):
    "Generate a list of random points within a square."
    
    # Fill a square with random points.
    mn, mx = 0, sqrLength
    P = []
    for i in xrange(numPoints):
	rand = random.randint
	y = rand(mn+1, mx-1)
	x = rand(mn+1, mx-1)
	P.append(complex(x, y))

    # Add some "outmost" corner points.
    if addCornerPoints != 0:
	P = P + [complex(min, min), complex(max, max), complex(min, max), complex(max, min)]

    return P


######################################################################
# Output
######################################################################

epsHeader = """%%!PS-Adobe-2.0 EPSF-2.0
%%%%BoundingBox: %d %d %d %d

/r 2 def                %% radius

/circle                 %% circle, x, y, r --> -
{
    0 360 arc           %% draw circle
} def

/cross                  %% cross, x, y --> -
{
    0 360 arc           %% draw cross hair
} def

1 setlinewidth          %% thin line
newpath                 %% open page
0 setgray               %% black color

"""

def saveAsEps(P, H, boxSize, path):
    "Save some points and their convex hull into an EPS file."
    
    # Save header.
    f = open(path, 'w')
    f.write(epsHeader % (0, 0, boxSize, boxSize))

    format = "%3d %3d"

    # Save the convex hull as a connected path.
    if H:
        f.write("%s moveto\n" % format % (H[0].real, H[0].imag))
        for p in H:
            f.write("%s lineto\n" % format % (p.real, p.imag))
        f.write("%s lineto\n" % format % (H[0].real, H[0].imag))
        f.write("stroke\n\n")

    # Save the whole list of points as individual dots.
    for p in P:
        f.write("%s r circle\n" % format % (p.real, p.imag))
        f.write("stroke\n")
            
    # Save footer.
    f.write("\nshowpage\n")


######################################################################
# Public interface
######################################################################

def convexHull(P):
    """Calculate the convex hull of a set of complex points.
    If the hull has a duplicate point, an exception will be raised.
    It is up to the application not to provide duplicates.
    """

    # Remove any duplicates
    points = list(set(P))
    points.sort(lambda a, b: 2*cmp(a.real, b.real)+cmp(a.imag, b.imag))

    # Build upper half of the hull.
    upper = [points[0], points[1]]
    for p in points[2:]:
	upper.append(p)
	while len(upper)>2 and not _isRightTurn(upper[-3:]):
	    del upper[-2]
    while len(upper)>2 and not _isRightTurn(upper[-2:]+upper[:1]):
    	del upper[-1]

    points.reverse()
    # Build lower half of the hull.
    lower = [points[0], points[1]]
    for p in points[2:]:
	lower.append(p)
	while len(lower)>2 and not _isRightTurn(lower[-3:]):
	    del lower[-2]
    while len(lower)>2 and not _isRightTurn(lower[-2:]+lower[:1]):
    	del lower[-1]
    us = set(upper)
    for q in lower:
    	if q not in us:
		upper.append(q)

    return tuple(upper)


######################################################################
# Test
######################################################################

def test():
    a = 200
    p = _makeRandomData(300, a, 0)
    c = convexHull(p)
    saveAsEps(p, c, a, "foo.eps")

# test()

######################################################################

if __name__ == '__main__':
    try:
        numPoints = int(sys.argv[1])
        squareLength = int(sys.argv[2])
        path = sys.argv[3]
    except IndexError:
        numPoints = 30
        squareLength = 200
        path = "sample.eps"

    p = _makeRandomData(numPoints, squareLength, addCornerPoints=0)
    c = convexHull(p)
    saveAsEps(p, c, squareLength, path)


