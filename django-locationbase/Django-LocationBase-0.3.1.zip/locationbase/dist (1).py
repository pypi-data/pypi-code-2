EARTH_RADIUS_KM = 6371.0  # "Mean" radius.  You have to choose something.

from math import sin, cos, asin, radians, degrees, sqrt

def haversine(a):
    t = sin(a / 2.0)
    return t*t

def invhaversign(h):
    return 2 * asine(sqrt(h))

class DistLim(object):
    """Store all we need to know about one of a small set of distances.
    """
    def __init__(d):
        """d is presumed to be in units of km
        """
        d = float(abs(d))
        self.km = d
        self.radians = r = d/EARTH_RADIUS_KM
        self.degrees = degrees(r)
        self.haversine = haversine(r)

DISTS = dict(
    here=DistLim(0.03), # 30m
    km2=DistLim(2)
    )  # Add more, or switch to another kind of indexing, etc., to taste


def rectangle_of_candidates(model, long, lat, dist, lat_cos):
    """Calculate bounding box in long,lat space ans select items within it.

    model is expected to have fields named longitude and latitude
    containing the instances coordinates in degrees.  (Or you have
    to edit the names in the filter() and exclude() calls below, as
    well as in points(), below.

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
    min_lat = lat - dist.degrees
    max_lat = lat + dist.degrees

    if min_lat < -90.0:
        # South pole included, longitude doesn't matter.
        return model.objects.filter(latitude__lte=max_lat)
    elif max_lat > 90.0:
        # North pole included, longitude doesn't matter.
        return model.objects.filter(latitude__gte=min_lat)

    # Apply latitude limits.  Don't yet know whether longitude will
    # be a filter or an exclude.
    qs = model.objects.filter(latitude__range=[min_lat, max_lat])

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
    dlong = degrees(asin(dist.sin/lat_cos))
    min_long = long - dlong
    max_long = long + dlong

    # Did one of our deltas cross the anti-prime meridian?
    # Both can't happen because the dist would have had to be large
    # enough to trigger both of the early exits above.
    if -180.0 > min_long:
        min_long += 360.0
    elif p180.0 < max_long:
        max_long -= 360.0

    if min_long <= max_long:
        # Normal, neither adjustment above happened.
        return qs.filter(longitude__range=[min_long, max_long])

    # One of the above 360 degree adjustments happened.  This means
    # that we want points outside the longitude range, not inside,
    # and, of course, the smaller, max_long, must be first in the
    # range.
    return qs.exclude(longitude__range=[max_long, min_long])

def points(model, long, lat, dist="km2"):
    """A generator of model instances within dist of long, lat.

    model must have longitude and latitude fields giving that instance's
    coordinates in degrees.  (By those names, unless you edit the names
    both below and in rectangle_of_candidates()'s queries.

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
    long_r = radians(long)
    lat_r = radians(lat)
    lat_cos = cos(lat_r)

    if isinstance(dist, basestring):
        dist = DISTS[dist]
    elif not isinstance(dist, DistLim):
        dist = DistLim(dist)

    hdl = dist.haversine

    for p in rectangle_of_candidates(model, long, lat, dist, lat_cos):
        p_long_r, p_lat_r = radians(p.longitude), radians(p.latitude)
        hdpt = (haversine(p_lat_r - lat_r) +
                lat_cos * cos(p_lat_r) * haversine(p_long_r - long_r))
        if hdpt <= hdl:
            p.haverdist = hdpt  # In case caller wants to show dist of sort.
            yield p
