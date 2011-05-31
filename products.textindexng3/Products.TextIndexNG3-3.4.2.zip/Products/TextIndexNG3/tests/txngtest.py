###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
TextIndexNG3 test layer

$Id: txngtest.py 2144 2009-03-15 17:41:50Z yvoschu $
"""

from Products.Five import zcml
from zope.testing.cleanup import cleanUp


class TextIndexNG3ZCMLLayer:

    @classmethod
    def setUp(cls):
        import Products.Five
        import Products.TextIndexNG3

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.Five)
        try:
            import Products.GenericSetup
            zcml.load_config('meta.zcml', Products.GenericSetup)
        except ImportError:
            pass
        zcml.load_config('configure.zcml', Products.TextIndexNG3)

    @classmethod
    def tearDown(cls):
        cleanUp()

# Derive from ZopeLite layer if available
try:
    from Testing.ZopeTestCase.layer import ZopeLite
except ImportError:
    pass # BBB: Zope < 2.11
else:
    TextIndexNG3ZCMLLayer.__bases__ = (ZopeLite,)
