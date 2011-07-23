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

class PsifasException(Exception): pass

class EndOfStreamException(PsifasException): pass

class Contradiction(PsifasException): pass

class InfiniteRecursionException(PsifasException): pass

class MergeException(PsifasException): pass

class DecipherException(PsifasException): pass

class DereferenceException(PsifasException): pass
