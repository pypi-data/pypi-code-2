"""
A timezone loader that uses a zip file.

This was taken more or less directly from gae-pytz.

Original Author: Rodrigo Moraes
"""
import os
import zipfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

zoneinfo = None
zoneinfo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
    'zoneinfo.zip'))


def get_zoneinfo():
    """Cache the opened zipfile in the module."""
    global zoneinfo
    if zoneinfo is None:
        zoneinfo = zipfile.ZipFile(zoneinfo_path)

    return zoneinfo


class ZipLoader(object):
    """A loader that that reads timezones using ZipFile."""
    def __init__(self):
        self.available = {}

    def open_resource(self, name):
        """Opens a resource from the zoneinfo subdir for reading."""
        name_parts = name.lstrip('/').split('/')
        if os.path.pardir in name_parts:
            raise ValueError('Bad path segment: %r' % os.path.pardir)

        zonedata = get_zoneinfo().read('zoneinfo/' + '/'.join(name_parts))
        return StringIO(zonedata)

    def resource_exists(self, name):
        """Return true if the given resource exists"""
        if name not in self.available:
            try:
                get_zoneinfo().getinfo('zoneinfo/' + name)
                self.available[name] = True
            except KeyError:
                self.available[name] = False

        return self.available[name]
