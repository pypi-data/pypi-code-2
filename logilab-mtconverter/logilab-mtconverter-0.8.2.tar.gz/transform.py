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
"""base transformation objects"""

__docformat__ = "restructuredtext en"


class Transform(object):
    """a transform is converting some content in a acceptable MIME type
    into another MIME type
    """
    name = None
    inputs = ()
    output = None
    input_encoding = None
    output_encoding = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        if not getattr(self, 'name', None):
            self.name = self.__class__.__name__

    def convert(self, trdata):
        """convert the given data structure into transform output's mime type

        :param trdata: `TransformData`
        :rtype: `TransformData`
        """
        # this is not true when transform accept wildcard
        #assert trdata.mimetype in self.inputs
        trdata.data = self._convert(trdata)
        trdata.mimetype = self.output
        if self.output_encoding:
            trdata.encoding = self.output_encoding
        return trdata

    def _convert(self, trdata):
        raise NotImplementedError


class TransformsChain(list):
    """A chain of transforms used to transform data"""

    inputs = ('application/octet-stream',)
    output = 'application/octet-stream'
    name = None

    def __init__(self, name=None, *args):
        list.__init__(self, *args)
        if name is not None:
            self.name = name
        if args:
            self._update()

    def convert(self, trdata):
        for transform in self:
            trdata = transform.convert(trdata)
        return trdata

    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self._update()

    def append(self, value):
        list.append(self, value)
        self._update()

    def insert(self, *args):
        list.insert(*args)
        self._update()

    def remove(self, *args):
        list.remove(*args)
        self._update()

    def pop(self, *args):
        list.pop(*args)
        self._update()

    def _update(self):
        self.inputs = self[0].inputs
        self.output = self[-1].output
        for i in range(len(self)):
            if hasattr(self[-i-1], 'output_encoding'):
                self.output_encoding = self[-i-1].output_encoding
                break
        else:
            try:
                del self.output_encoding
            except:
                pass
