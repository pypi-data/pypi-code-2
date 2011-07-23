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

from base import *
from arithmetic import *
from switch import *
from utils import *
from multifield import MultiField

from itertools import count

class Repeater(Psifas):
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

    def _all_fields(self, location):
        counter = location.context(self._fields[0].name(self, location)).value
        any_more_fields = False
        
        if is_abstract(counter):
            # we may not know the counter, but we can estimate how many extra fields
            # are needed atleast.
            repeat_list = location.context('.').value
            if is_sequence_type(repeat_list):
                counter = len(repeat_list)
            elif isinstance(repeat_list, SparseList):
                counter = repeat_list.min_length()
                any_more_fields = True
            else:
                return self._fields, True
        return self._fields + tuple(Field(str(index), self.sub_psifas) for index in xrange(counter)), any_more_fields

    def _decipher(self, location, repeat_list, counter, *sub_values):
        repeat_list = location.imerge(repeat_list, SparseList(sub_values))
        if is_sequence_type(repeat_list):
            counter = location.imerge(counter, len(repeat_list))
        elif not is_abstract(counter):
            repeat_list = location.imerge(repeat_list, BottomTuple(counter))
        return (repeat_list, counter) + tuple(repeat_list[:len(sub_values)])

class _RepeatUntilTermCounter(Psifas):
    def __init__(self, stop_repeat_field_name):
        super(_RepeatUntilTermCounter, self).__init__()
        self.stop_repeat_field_name = stop_repeat_field_name
        
    def _decipher_location_set(self, location, all_fields):
        counter = location.context().value
        if is_abstract(counter):
            for index in count():
                stop_repeat = location.context('../%s/%s' % (index, self.stop_repeat_field_name)).value
                if is_abstract(stop_repeat):
                    break
                elif stop_repeat is True:
                    location.set_context_value(index + 1)
                    break
        elif counter > 0:
            for index in xrange(counter - 1):
                location.set_context_value(False, '../%s/%s' % (index, self.stop_repeat_field_name))
            location.set_context_value(True, '../%s/%s' % (counter - 1, self.stop_repeat_field_name))
        return (counter,)

    def _decipher_location(self, location, all_fields):
        counter, = self._decipher_location_set(location, all_fields)
        return not is_abstract(counter)

class RepeatUntilTerm(Repeater):
    def __init__(self, sub_psifas, stop_repeat, stop_repeat_field_name = None):
        if stop_repeat_field_name is None:
            stop_repeat_field_name = '.stop_repeat'
            
        super(RepeatUntilTerm, self).__init__(_RepeatUntilTermCounter(stop_repeat_field_name), 
                                              Psifas(Field('.$repeater', sub_psifas),
                                                     Field(stop_repeat_field_name, stop_repeat),
                                                     spiritual = True)
                                              )
        self.sub_psifas_continue = Psifas(Field('.$repeater', sub_psifas),
                                          Field(stop_repeat_field_name, stop_repeat),
                                          Field(stop_repeat_field_name, Constant(False)),
                                          spiritual = True)

        self.sub_psifas_stop = Psifas(Field('.$repeater', sub_psifas),
                                      Field(stop_repeat_field_name, stop_repeat),
                                      Field(stop_repeat_field_name, Constant(True)),
                                      spiritual = True)
        
        self._stop_repeat_field_name = stop_repeat_field_name

    def _explicit_replace(self, old_psifas, new_psifas):
        if old_psifas is self.sub_psifas:
            self.sub_psifas = new_psifas
        else:
            self.sub_psifas.replace(old_psifas, new_psifas)

        if old_psifas is self.sub_psifas_continue:
            self.sub_psifas_continue = new_psifas
        else:
            self.sub_psifas_continue.replace(old_psifas, new_psifas)

        if old_psifas is self._sub_psifas_stop:
            self._sub_psifas_stop = new_psifas
        else:
            self._sub_psifas_stop.replace(old_psifas, new_psifas)

    def _all_fields(self, location):
        counter = location.context(self._fields[0].name(self, location)).value
        any_more_fields = False
        
        if is_abstract(counter):
            # we may not know the counter, but we can estimate how many extra fields
            # are needed atleast.
            repeat_list = location.context('.').value
            if is_sequence_type(repeat_list):
                counter = len(repeat_list) # TODO: what if less then 1?
            elif isinstance(repeat_list, SparseList):
                counter = max(1, repeat_list.min_length())
                any_more_fields = True
            else:
                counter = 1
                any_more_fields = True
        if location.context('%s/%s' % (counter - 1, self._stop_repeat_field_name)).value is False:
            counter += 1
            any_more_fields = True
        return (self._fields +
                tuple(Field(str(index), self.sub_psifas_continue) for index in xrange(counter - 1)) +
                (Field(str(counter - 1), self.sub_psifas if any_more_fields else self.sub_psifas_stop),)), any_more_fields

class RepeatUntil(ConcretePsifas):
    def __init__(self, sub_psifas, last_element, including = True):
        super(RepeatUntil, self).__init__(UniqueField('.until_term', RepeatUntilTerm(sub_psifas, Equal(This, last_element))))
        self.including = including
        self._last_element = last_element

    def _decipher(self, location, value, until_term):
        if until_term is not Bottom:
            if self.including:
                value = until_term
            else:
                value = until_term[:-1]
        elif value is not Bottom:
            if self.including:
                until_term = value
            else:
                until_term = tuple(value) + (self._last_element,)
        return value, until_term

class CString(String):
    def __init__(self):
        super(CString, self).__init__(RepeatUntil(Segment(1), '\x00', including = False))

class PascalString(Segment):
    def __new__(cls, *args, **kws):
        # don't use the Segment's __new__
        return Psifas.__new__(cls)

    def __init__(self, sizer_size = 1, sizer_format = UBInt):
        super(PascalString, self).__init__(sizer_format(Segment(sizer_size)))
