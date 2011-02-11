"""DRH TEST APPLICATION

Copyright (c) 2003-2004 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from cubicweb.devtools.testlib import AutomaticWebTest
class AutomaticWebTest(AutomaticWebTest): pass

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
