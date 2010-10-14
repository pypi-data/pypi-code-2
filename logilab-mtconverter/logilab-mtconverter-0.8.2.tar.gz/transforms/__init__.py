# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# copyright 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of logilab-mtconverter.
#
# logilab-mtconverter is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# logilab-mtconverter is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with logilab-mtconverter. If not, see <http://www.gnu.org/licenses/>.
"""some basic transformations (pure python)

"""
__docformat__ = "restructuredtext en"

import re

from logilab.mtconverter import xml_escape
from logilab.mtconverter.transform import Transform

class IdentityTransform(Transform):
    """identity transform: leave the content unchanged"""
    def _convert(self, trdata):
        return trdata.data


class text_to_text(IdentityTransform):
    inputs = ('text/*',)
    output = 'text/plain'


class rest_to_text(Transform):
    inputs = ('text/rest', 'text/x-rst')
    output = 'text/plain'

    def _convert(self, trdata):
        res = []
        for line in trdata.data.splitlines():
            sline = line.lstrip()
            if sline.startswith('.. '):
                continue
            res.append(line)
        return '\n'.join(res)


_TAG_PROG = re.compile(r'</?.*?>', re.U)
class xml_to_text(Transform):
    inputs = ('application/xml',)
    output = 'text/plain'

    def _convert(self, trdata):
        return _TAG_PROG.sub(' ', trdata.data)


class text_to_html(Transform):
    inputs = ('text/plain',)
    output = 'text/html'

    def _convert(self, trdata):
        res = ['<p>']
        for line in trdata.data.splitlines():
            line = line.strip()
            if not line:
                if not res[-1].endswith('<p>'):
                    res.append('</p><p>')
            else:
                res.append(xml_escape(line) + '<br/>')
        res.append('</p>')
        return '\n'.join(res)


class text_to_html_pre(Transform):
    """variant for text 2 html transformation : simply wrap text into pre tags
    """
    inputs = ('text/plain',)
    output = 'text/html'

    def _convert(self, trdata):
        res = ['<pre>']
        res.append(xml_escape(trdata.data))
        res.append('</pre>')
        return '\n'.join(res)


class xlog_to_html(Transform):
    inputs = ('text/x-log',)
    output = 'text/html'

    def _convert(self, trdata):
        return '\n'.join([xml_escape(x)+'<BR/>' for x in trdata.data.splitlines()])
