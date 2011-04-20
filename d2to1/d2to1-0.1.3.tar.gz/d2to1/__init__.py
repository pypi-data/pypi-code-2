import pkg_resources
try:
    __version__ = pkg_resources.get_distribution('d2to1').version
except pkg_resources.DistributionNotFound:
    __version__ = None
