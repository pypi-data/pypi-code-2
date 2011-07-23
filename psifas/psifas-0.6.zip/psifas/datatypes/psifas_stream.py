# Copyright 2010 Oren Zomer <oren.zomer@gmail.com>
#
# This file is part of pypsifas.

# pypsifas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pypsifas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pypsifas.  If not, see <http://www.gnu.org/licenses/>.

from datatypes.pretty import Pretty

class PsifasStream(Pretty):
    __slots__ = ['stream']
    def __init__(self, stream):
        super(PsifasStream, self).__init__()
        if isinstance(stream, str):
            stream = BytesIO(stream)
        self.stream = stream

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def read(self, size, best_effort = False):
        first_part = self.stream.read(size)
        size -= len(first_part)
        all_parts = []
        while size > 0:
            # usually doesn't happen
            new_part = self.stream.read(size)
            if new_part == '':
                if best_effort:
                    break
                # seek back? self.stream.seek(-len(first_part) - sum(map(len, all_parts)), SEEK_CUR)
                raise EndOfStreamException()
            size -= len(new_part)
        return first_part + ''.join(all_parts)

    def read_all(self):
        all_parts = [self.stream.read()]
        new_part = self.stream.read()
        while new_part != '':
            all_parts.append(new_part)
            new_part = self.stream.read()
        return ''.join(all_parts)

    def is_eof(self):
        c = self.stream.read(1)
        if len(c) == 0:
            return True
        self.stream.seek(-1, SEEK_CUR)
        return False

    def __deepcopy__(self, memo):
        return self


            
