import pkg_resources

try:
    ZOPE2_VERSION = pkg_resources.get_distribution('Zope2').version
except pkg_resources.DistributionNotFound:
    ZOPE2_VERSION = 0.0
