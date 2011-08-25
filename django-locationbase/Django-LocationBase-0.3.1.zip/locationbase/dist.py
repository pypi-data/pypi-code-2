# Credits : Bill Freeman ke1g.nh@gmail.com
from math import sin, cos, asin, radians, pi, sqrt

EARTH_RADIUS_KM = 6371.0  # "Mean" radius.  You have to choose something.

two_pi = 2.0 * pi
half_pi = pi / 2.0

class DistLim(object):
    """Store all we need to know about one of a small set of distances.
    """
    def __init__(d):
        """d is presumed to be in units of km
        """
        d = float(abs(d))
        self.km = d
        self.radians = d/EARTH_RADIUS_KM

DISTS = dict(
    here=DistLim(0.03), # 30m
    km2=DistLim(2)
    )  # Add more, or switch to another kind of indexing, etc., to taste


def rectangle_of_candidates(model, long_r, lat_r, dist, lat_cos):
    """Calculate bounding box in long,lat space ans select items within it.

    model is expected to have fields named long_r and lat_r containing
    the instances coordinates in radians.

    The model might also have longitude and latitude in other units,
    for stability of display, this code doesn't care.  Or it may be
    happy with applying math.degrees() for any management interface.
    The difficulty of the latter is that converting to and from
    radians won't, in general, return the identical number: there will
    be differences in low order places, which might confuse a human
    operator.

    long_r and lat_r are the center of a distance circle of radius
    dist.radians.  All are expressed in radians.  They are used in
    radian form in other calculations, so it is presumed that it is
    best to let the caller translate them, if necessary, from, say,
    degrees, to radians once, rather than having each sub function or
    code section calculate them redundantly.

    dist.sin is the sin of the radius of the distance circle
    expressed as radians of great circle arc.  Since it is presumed
    that only a limited number of distance values are to be used,
    it is best to precalculate them once per site start up, rather
    than for each function or even each query.

    lat_cos is cos(lat_r), also presumed to have been calculated
    by the caller for multiple usages.

    returns a query set that will find objects within the bounding
    box.
    """
    min_lat = lat_r - dist.radians
    max_lat = lat_r + dist.radians

    if min_lat < -half_pi:
        # South pole included, longitude doesn't matter.
        return model.objects.filter(lat_r__lte=max_lat)
    elif max_lat > half_pi:
        # North pole included, longitude doesn't matter.
        return model.objects.filter(lat_r__gte=min_lat)

    # Apply latitude limits.  Don't yet know whether longitude will
    # be a filter or an exclude.
    qs = model.objects.filter(lat_r__range=[min_lat, max_lat])

    # The following is derived from the spherical right triangle
    # formula sin(a) = sin(A)sin(c), where A is an asimuth angle
    # measured at the North pole (which is thus a longitude difference),
    # a is the opposite side, which is our distance in radians, and
    # c is the compliment of our latitude, so cos(lat) == sin(c).
    # The right angle of the right triangle is the corner that is
    # neither the pole nor the center of the distance circle, so the
    # distance radius great circle meets the third side, a longitude
    # line, at right angles, so that longitude line is tangent to the
    # distance circle.
    dlong = asin(dist.sin/lat_cos)
    min_long = long_r - dlong
    max_long = long_r + dlong

    # Did one of our deltas cross the anti-prime meridian?
    # Both can't happen because the dist would have had to be large
    # enough to trigger both of the early exits above.
    if -pi > min_long:
        min_long += two_pi
    elif pi < max_long:
        max_long -= two_pi

    if min_long <= max_long:
        # Normal, neither adjustment above happened.
        return qs.filter(long_r__range=[min_long, max_long])

    # One of the above two_pi adjustments happened.  This means that
    # we want points outside the longitude range, not inside, and,
    # of course, the smaller, max_long, must be first in the range.
    return qs.exclude(long_r__range=[max_long, min_long])

def haversine(a):
    t = sin(a / 2.0)
    return t*t

def invhaversign(h):
    return 2 * asine(sqrt(h))

def points(model, long, lat, dist="km2"):
    """A generator of model instances within dist of long, lat.

    model must have long_r and lat_r fields giving that instance's
    coordinates in radians.

    long and lat are in degrees.  It's easy enough to rewrite this
    for other units if you like.

    dist is one of:
      An index into DISTS, above.
      A DistLim instance.
      A number of kilometers (int or float).

    Use like:
      for p in points(...):
        ...

      or:
        pts = list(points(...))
        pts.sort()
        for p in pts:
          ...
    """
    return points_r(model, radians(long), radians(lat), dist="km2")

def points_r(model, long_r, lat_r, dist="km2"):
    """See points, except long_r and lat_r are in radians
    """
    lat_cos = cos(lat_r)

    if isinstance(dist, basestring):
        dist = DISTS[dist]
    elif not isinstance(dist, DistLim):
        dist = DistLim(dist)

    hdl = haversine(dist.radians)

    for p in rectangle_of_candidates(model, long_r, lat_r, dist, lat_cos):
        hdpt = (haversine(p.lat_r = lat_r) + lat_cos * cos(p.lat_r) * haversine(p.long_r - long_r))
        if hdpt <= hdl:
            p.haverdist = hdpt  # In case caller wants to show dist of sort.
            yield p