import version
import os

__version__ = VERSION = version.VERSION
__doc__ = open(os.path.join(os.path.dirname(__file__), 'README')).read()
__docformat__ = 'reStructuredText'