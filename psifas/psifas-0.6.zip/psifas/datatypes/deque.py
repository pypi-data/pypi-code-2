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

from collections import deque as _deque

try:
    _deque(maxlen=1)
except TypeError:
    class LimitedDeque(_deque):
        def __init__(self, iterable, maxlen):
            _deque.__init__(self, iterable)
            self.__maxlen = maxlen
            
        def appendleft(self, *args, **kw):
            try:
                return _deque.appendleft(self, *args, **kw)
            finally:
                if len(self) > self.__maxlen:
                    _deque.pop(self)

        def extendleft(self, var):
            try:
                return _deque.extendleft(self, var)
            finally:
                while len(self) > self.__maxlen:
                    _deque.pop(self)
            
        def append(self, *args, **kw):
            try:
                return _deque.append(self, *args, **kw)
            finally:
                if len(self) > self.__maxlen:
                    _deque.popleft(self)

        def extend(self, var):
            try:
                return _deque.extend(self, var)
            finally:
                while len(self) > self.__maxlen:
                    _deque.popleft(self)

    def deque(iterable = (), maxlen = None):
        if maxlen is None:
            return _deque(iterable)
        return LimitedDeque(iterable, maxlen)
else:
    deque = _deque
