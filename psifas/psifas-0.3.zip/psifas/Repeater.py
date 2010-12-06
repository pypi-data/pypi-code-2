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

from Base import *
from Base import _NeverFinishHoldStream
from Arithmetic import *
from Switch import *

class _NeverFinishFixedRepeater(_NeverFinishHoldStream):
    def __init__(self, counter, sub_psifas):
        super(_NeverFinishFixedRepeater, self).__init__(*(Field(str(index), sub_psifas) for index in xrange(counter)))

    def _decipher(self, value, *sub_values):
        if value is not NoValue:
            return (value,) + tuple(value)
        return super(_NeverFinishFixedRepeater, self)._decipher(value, *sub_values)

class _FixedRepeater(_NeverFinishFixedRepeater):
    def _parse(self, *sub_values):
        return sub_values

    def _decipher_stream(self, location):
        # jump over parent:
        return Psifas._decipher_stream(self, location)

class Repeater(MappingSwitch):
    def __init__(self, counter, sub_psifas):
        if isinstance(counter, str):
            counter = Link(counter)
        super(Repeater, self).__init__(Field('counter', counter))
        self.sub_psifas = sub_psifas

    def _explicit_replace(self, old_psifas, new_psifas):
        if old_psifas is self.sub_psifas:
            self.sub_psifas = new_psifas
        else:
            self.sub_psifas.replace(old_psifas, new_psifas)

    def mapping(self, count):
        # TODO: make more efficient?
        return _FixedRepeater(count, self.sub_psifas)

    def reverse_mapping(self, solution_value):
        return len(solution_value)

class RepeatUntilTerm(MappingSwitch):
    def __init__(self, sub_psifas, stop_repeat):
        super(RepeatUntilTerm, self).__init__()
        self.stop_repeat_field_name = '.stop_repeat#%s' % (id(self),)
        self.sub_psifas = Psifas(Field('.$repeater', sub_psifas),
                                 Field(self.stop_repeat_field_name, stop_repeat),
                                 spiritual = True)

    def _explicit_replace(self, old_psifas, new_psifas):
        if old_psifas is self.sub_psifas:
            self.sub_psifas = new_psifas
        else:
            self.sub_psifas.replace(old_psifas, new_psifas)    

    def mapping_location(self, location):
        meta_sub_location = location[-1]
        if location.context().value is not NoValue:
            count = len(location.context().value)
            stop_repeat = True
        else:
            count = len(meta_sub_location)
            if count > 0:
                stop_repeat = meta_sub_location.context('%s/%s' % (count - 1, self.stop_repeat_field_name)).value
            else:
                count = 1
                stop_repeat = NoValue

        if not stop_repeat: # False or NoValue
            if stop_repeat is not NoValue:
                count += 1
            return _NeverFinishFixedRepeater(count, self.sub_psifas)

        for before_edge in xrange(count -1):
            meta_sub_location.context('%s/%s' % (before_edge, self.stop_repeat_field_name)).set_value(False, location)
        meta_sub_location.context('%s/%s' % (count - 1, self.stop_repeat_field_name)).set_value(stop_repeat, location)
        
        return _FixedRepeater(count, self.sub_psifas)

class RepeatUntil(Psifas):
    def __init__(self, sub_psifas, last_element, including = True):
        super(RepeatUntil, self).__init__(Field('.until_term#', RepeatUntilTerm(sub_psifas, Equal(Link('...'), last_element))))
        self.including = including
        self._last_element = last_element

    def _decipher(self, value, until_term):
        if until_term is not NoValue:
            if self.including:
                value = until_term
            else:
                value = until_term[:-1]
        elif value is not NoValue:
            if self.including:
                until_term = value
            else:
                until_term = tuple(value) + (self._last_element,)
        return value, until_term

class CString(String):
    def __init__(self):
        super(CString, self).__init__(RepeatUntil(Segment(1), '\x00', including = False))

class PascalString(Segment):
    def __init__(self, sizer_size = 1, sizer_format = UBInt):
        super(PascalString, self).__init__(sizer_format(Segment(sizer_size)))

            
