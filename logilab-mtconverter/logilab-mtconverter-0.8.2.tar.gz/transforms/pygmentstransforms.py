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
"""interface pygments (http://pygments.org/) with mtconverter"""

__docformat__ = "restructuredtext en"

from logilab.mtconverter.transform import Transform

from pygments import highlight
from pygments.lexers import LEXERS, get_lexer_for_mimetype as mtlexer
from pygments.formatters import HtmlFormatter, LatexFormatter, RtfFormatter, SvgFormatter

# hint: changes MIMETYPES before registering pygments transforms if you don't
#       want all available inputs
mimetypes = sorted(set([mt for _, _, _, _, mimetypes in LEXERS.itervalues()
                       for mt in mimetypes]))

class PygmentsHTMLTransform(Transform):
    """note: this transform use CSS classes which can be obtained using:
    formatter.get_style_defs()
    """
    inputs = mimetypes
    output = 'text/html'
    def _convert(self, trdata):
        lexer = mtlexer(trdata.mimetype, encoding=trdata.encoding)
        return highlight(trdata.decode(force=True), lexer, HtmlFormatter())


class PygmentsLatexTransform(Transform):
    inputs = mimetypes
    output = 'text/x-latex'
    def _convert(self, trdata):
        lexer = mtlexer(trdata.mimetype, encoding=trdata.encoding)
        return highlight(trdata.decode(force=True), lexer, LatexFormatter())


class PygmentsRTFTransform(Transform):
    inputs = mimetypes
    output = 'application/rtf'
    def _convert(self, trdata):
        lexer = mtlexer(trdata.mimetype, encoding=trdata.encoding)
        return highlight(trdata.decode(force=True), lexer, RtfFormatter())

class PygmentsSVGTransform(Transform):
    inputs = mimetypes
    output = 'image/svg+xml'
    def _convert(self, trdata):
        lexer = mtlexer(trdata.mimetype, encoding=trdata.encoding)
        return highlight(trdata.decode(force=True), lexer, SvgFormatter())


transform_classes = (PygmentsHTMLTransform, PygmentsLatexTransform,
                     PygmentsRTFTransform, PygmentsSVGTransform)
