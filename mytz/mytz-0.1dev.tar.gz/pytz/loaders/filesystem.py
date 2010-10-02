import os

try:
    from pkg_resources import resource_stream
except ImportError:
    resource_stream = None


class TimezoneLoader(object):
    def __init__(self):
        self.available = {}

    def open_resource(self, name):
        """Open a resource from the zoneinfo subdir for reading.

        Uses the pkg_resources module if available and no standard file
        found at the calculated location.
        """
        name_parts = name.lstrip('/').split('/')
        for part in name_parts:
            if part == os.path.pardir or os.path.sep in part:
                raise ValueError('Bad path segment: %r' % part)
        filename = os.path.join(os.path.dirname(__file__),
                                'zoneinfo', *name_parts)
        if not os.path.exists(filename) and resource_stream is not None:
            # http://bugs.launchpad.net/bugs/383171 - we avoid using this
            # unless absolutely necessary to help when a broken version of
            # pkg_resources is installed.
            return resource_stream(__name__, 'zoneinfo/' + name)
        return open(filename, 'rb')

    def resource_exists(self, name):
        """Return true if the given resource exists"""
        if name not in self.available:
            try:
                self.open_resource(name)
                self.available[name] = True
            except IOError:
                self.available[name] = False

        return self.available[name]
