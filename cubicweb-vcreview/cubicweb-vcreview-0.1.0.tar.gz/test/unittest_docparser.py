# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from logilab.common.testlib import TestCase, unittest_main, mock_object
from logilab.mtconverter import TransformData

from cubicweb import devtools
from cubicweb.mttransforms import ENGINE

from cubes.vcreview.docparser import Diff2HTMLTransform

class FakeRequest(object):
    def add_css(self, file): pass

class DiffParserTC(TestCase):
    def test_insert_point(self):
        def insert_point_cb(ipid, trdata, w):
            w('<hr class="%s"/>' % ipid)
            self.ipid = ipid
        ENGINE.add_transform(Diff2HTMLTransform(insert_point_cb))
        data = open(self.datapath('pytestgc.diff')).read()
        trdata = TransformData(data, 'text/x-diff', 'utf-8')
        trdata.appobject = mock_object(_cw=FakeRequest())
        htmldata = ENGINE.convert(trdata, 'text/annotated-html')
        self.assertEqual(self.ipid, '4')
        self.assertTrue(htmldata.data.startswith('<div class="text/x-diff">'))

if __name__ == '__main__':
    unittest_main()
