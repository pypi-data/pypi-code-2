import sys

import os.path

from io import StringIO
from os.path import (dirname, abspath)
from unittest import TestCase
from test import support

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
from tenpy.builder import TenpyBuilder


class TenpyBuilderTest(TestCase):

    def setUp(self):
        self.after = '<html>'\
                   '<head></head>'\
                   '<body>'\
                   'example1'\
                   + "".join(["loop example2" for s in range(5)]) +\
                   '<p id="p1">loop example3</p>'\
                   '<p id="p2">loop example4</p>'\
                   '<p id="p1">loop example3</p>'\
                   '<p id="p1">loop example3</p>'\
                   '<p id="p2">loop example4</p>'\
                   '<p id="p1">loop example3</p>'\
                   '<p id="p1">loop example3</p>'\
                   '<p id="p2">loop example4</p>'\
                   '<p id="p1">loop example3</p>'\
                   '<p id="p1">loop example3</p>'\
                   '<p id="p2">loop example4</p>'\
                   '<p id="p1">loop example3</p>'\
                   '<p id="p1">loop example3</p>'\
                   '<p id="p2">loop example4</p>'\
                   '<p id="p1">loop example3</p>'\
                   'example1'\
                   'testclass1'\
                   '&lt;&gt;"\'&amp;testescapes'\
                   'span only'\
                   '<div class="sc1">spanclass1</div>'\
                   '0'\
                   '1'\
                   'true'\
                   '<p id="lp1">exists1</p>'\
                   '<p id="lp2">loop with missing test2</p>'\
                   'nl0'\
                   'nl1'\
                   '<p id="after_with">after with complete</p>'\
                   'nl0'\
                   'nl1'\
                   '<p id="after_with">after with complete</p>'\
                   '<p id="more_nested">'\
                   '<p id="nested_inner">more nested complete</p>'\
                   'mnil1'\
                   'mnil2'\
                   'mnil3'\
                   '</p>'\
                   'mnl1'\
                   'mnl2'\
                   'mnl3'\
                   '<newtag attr="val">text</newtag>'\
                   '<a id="attr" href="http://www.naniyueni.org/">replace attribute test</a>'\
                   'v1testv2test'\
                   'eval test success'\
                   '</body>'\
                   '</html>'

        self.include_after = '<html>'\
                             '<head></head>'\
                             '<body>'\
                             '<div>include complete</div>'\
                             'include build complete'\
                             '</body>'\
                             '</html>'
        self.builder = TenpyBuilder()

    def test_build(self):
        html = self.builder.build(os.path.join(dirname(__file__), "test.html"),
                var1="v1test", var2="v2test")
        html = "".join([s.strip() for s in html.split("\n")])
        self.assertEqual(html, self.after)

    def test_build_include(self):
        html = self.builder.build(os.path.join(dirname(__file__),
            'test_include1.html'))
        html = "".join([s.strip() for s in html.split("\n")])
        self.assertEqual(html, self.include_after)


def test_main():
    support.run_unittest(TenpyBuilderTest)

if __name__ == "__main__":
    test_main()
