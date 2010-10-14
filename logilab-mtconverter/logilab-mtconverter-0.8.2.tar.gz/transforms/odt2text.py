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
"""odt2text: Turn odt file into equivalent plain text file.
Copyright (C) 2009 Logilab S.A.
"""
from zipfile import ZipFile
from lxml import etree
from tempfile import TemporaryFile as tmpfile

from logilab.mtconverter.transform import Transform

class odt_to_unformatted_text(Transform):
    """transforms odt content to unformatted plain text"""

    name = "odt_to_text"
    inputs  = ("application/vnd.oasis.opendocument.text",)
    output = "text/plain"

    def _convert(self, trdata):
        data = trdata.data
        # XXX ZipFile should also accept a string
        #     however, there is some bug within
        #     so we feed it a file
        if isinstance(data, str):
            tmp = tmpfile(mode='w+b')
            tmp.write(data)
            tmp.seek(0)
            data = tmp
        # /XXX
        zip = ZipFile(data, 'r')
        alltext = []
        for subelt in ('content.xml', 'meta.xml'):
            root = etree.fromstring(zip.read(subelt))
            for node in root.iter():
                for attr in ('text', 'tail'):
                    text = getattr(node, attr)
                    if text:
                        text = text.strip()
                        if text:
                            alltext.append(text)
        return u' '.join(alltext)
