"""some utilities for testing forge security

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubes.tracker.testutils import SecurityTC

class ForgeSecurityTC(SecurityTC):

    def setUp(self):
        SecurityTC.setUp(self)
        # implicitly test manager can add some entities
        self.execute('INSERT License X: X name "license"')
        self.execute('INSERT ExtProject X: X name "projet externe"')
        self.commit()
