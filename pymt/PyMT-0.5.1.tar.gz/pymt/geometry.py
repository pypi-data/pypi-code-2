'''
Geometry: facilities functions for geometry calculations
'''
__all__ = ('circumcircle', 'minimum_bounding_circle')

from pymt.vector import Vector

def circumcircle(a, b, c):
    '''
    Computes the circumcircle of a triangel defined by a,b,c
    see: http://en.wikipedia.org/wiki/Circumscribed_circle#Circumscribed_circles_of_triangles
    
    :Parameters:
        `a` : iterable
            the 1. point of the triangle
        `b` : iterable
            the 2. point of the triangle
        `c` : iterable
            the 3. point of the triangle
        
    :Return:
        A Circle that defined the tuple :
            * The first element in the returned touple is the center (tuple x,y)
            * The second the radius (float)
    '''
    P = Vector(a[0], a[1])
    Q = Vector(b[0], b[1])
    R = Vector(c[0], c[1])

    mPQ = (P+Q)*.5
    mQR = (Q+R)*.5
    
    numer = -(-mPQ.y*R.y + mPQ.y*Q.y + mQR.y*R.y - mQR.y*Q.y \
              -mPQ.x*R.x + mPQ.x*Q.x + mQR.x*R.x - mQR.x*Q.x)
    denom =  (-Q.x*R.y + P.x*R.y - P.x*Q.y + Q.y*R.x - P.y*R.x + P.y*Q.x)
    
    t = numer/denom
    
    cx  = -t * (Q.y - P.y) + mPQ.x
    cy  =  t * (Q.x - P.x) + mPQ.y
    
    return ((cx, cy), (P - (cx, cy)).length())
    
    
def minimum_bounding_circle(points):
    '''
    Returns the minimum bounding circle for a set of points
    
    For a description of the problem being solved see http://en.wikipedia.org/wiki/Smallest_circle_problem
    The function uses Applet's Algorithm Algorithm, worst case teh runtime is O(h^3 *n), where h= number of points in teh convex hull of the set of points. But it runs in linear time in almost all real world cases.
    see: http://www.personal.kent.edu/~rmuhamma/Compgeometry/MyCG/CG-Applets/Center/centercli.htm
    
    :Parameters:
        `points` : iterable
            A list of points (2 tuple with x,y coordinates)

    :Return:
        A Circle that defined the tuple :
            * The first element in the returned touple is the center (tuple x,y)
            * The second the radius (float)
    '''
    points = [Vector(p[0], p[1]) for p in points]
    
    if len(points) == 1:
        return (points[0].x, points[0].y), 0.0
        
    if len(points) == 2:
        p1, p2 = points
        return (p1+p2)*.5, ((p1-p2)*.5).length()

    # determine a point P with the smallest y value
    P = min(points, key=lambda p:p.y)
    
    # find a point Q such that the angle of the line segment
    # PQ with the x axis is minimal
    def x_axis_angle(q):
        if q == P:
            return 1e10 # max val if teh same, to skip
        return abs( (q - P).angle((1, 0)) ) 
    Q = min(points, key=x_axis_angle)
    
    for p in points:
        # find R such that angle PRQ is minimal
        def angle_pq(r):
            if r in (P, Q):
                return 1e10 # max val if teh same, to skip
            return abs(  (r - P).angle(r - Q) )
        R = min(points, key=angle_pq)

        # check for case 1 (angle PRQ is obtuse), the circle is determined
        # by two points, P and Q. radius = |(P-Q)/2|, center = (P+Q)/2
        if angle_pq(R) > 90.0:
            return (P+Q)*.5, ((P-Q)*.5).length()
        
        # if angle RPQ is obtuse, make P = R, and try again
        if abs((R-P).angle(Q-P)) > 90:
            P = R
            continue
    
        # if angle PQR is obtuse, make Q = R, and try again
        if abs((P-Q).angle(R-Q)) > 90:
            Q = R
            continue
   
        # all angles were acute..we just need teh circle through the
        # two points furthest apart!
        break
    
    # find teh circumcenter for triangle given by P,Q,R
    return circumcircle(P, Q, R)
   
    
