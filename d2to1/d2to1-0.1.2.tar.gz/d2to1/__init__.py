import pkg_resources
try:
    __version__ = pkg_resources.require('d2to1')[0].version
except pkg_resources.DistributionNotFound:
    __version__ = None
