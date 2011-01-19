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

from utils import *
from base import *
import operator

class MultiField(Psifas):
    name_validity = {}
    name_validity_max_size = 10**4

    def __init__(self, first_arg, *args, **kw):
        if isinstance(first_arg, Field):
            fields = (first_arg,) + args
        elif isinstance(first_arg, str):
            fields = []
            field_name = first_arg
            for arg in args:
                if isinstance(arg, str):
                    field_name = arg
                else:
                    fields.append(Field(field_name, arg))
        else:
            fields = [Field(tup[0], sub_psifas) for tup in (first_arg,) + args for sub_psifas in tup[1:]]

        self.payload_field_name = kw.pop('payload_field_name', None)
        if self.payload_field_name is not None:
            fields.append(Field(self.payload_field_name, Psifas()))

        super(MultiField, self).__init__(*fields, **kw)

    def _decipher_location(self, location):
        super(MultiField, self)._decipher_location(location)

        if self.payload_field_name is not None:
            payload = location.payload
            if payload is not None:
                location.context(self.payload_field_name).set_value(payload, location)
            else:
                payload = location.context(self.payload_field_name).value
                if payload is not NoValue:
                    location.set_payload(payload)

    @classmethod
    def is_valid_name(cls, name):
        validity = cls.name_validity.get(name, None)
        if validity is not None:
            return validity
        if len(cls.name_validity) >= cls.name_validity_max_size:
            cls.name_validity.clear()
        # based on the pythonic falseness of ''.isalnum()
        cls.name_validity[name] = validity = name.replace('_', 'a').isalnum() and (not name[0].isdigit()) and not hasattr(Container, name)
        return validity

    def _parse(self, *values):
        return Container()

class Struct(MultiField):
    spiritual = True

    def _decipher(self, container, *values):
        container, _ = imerge(container,
                          Container(*((field.name, value) for (field, value) in izip(self._fields, values)
                                    if self.is_valid_name(field.name) and value is not NoValue)))

        for field, value in izip(self._fields, values):
            if field.name in ('', '.'):
                container, _ = imerge(container, value)

        yield container

        for field, value in izip(self._fields, values):
            # because we merged the container with the values, there's no
            # need in remerging the values with the container's attributes.
            if self.is_valid_name(field.name):
                container_attribute = getattr(container, field.name, NoValue)
                if container_attribute is not NoValue:
                    value, _ = imerge(value, container_attribute)
            elif field.name in ('', '.'):
                value, _ = imerge(value, container)
            yield value

class BitField(Struct):
    def __init__(self, target, *size_names, **kw):
        if isinstance(target, str):
            target = Link(target)
        bit_mask_offset = 0

        super(BitField, self).__init__(Field(self.unique('.bitfield'), target),
                                       *[Field(name, Psifas()) for size, name in size_names], **kw)
        sizes, names = zip(*size_names)
        offsets = [sum(sizes[:index]) for index in xrange(0, len(sizes))]
        self.name_mask_offsets = zip(names, [(1 << size) - 1 for size in sizes], offsets)

    def _decipher(self, container, bit_field, *values):
        if not isinstance(bit_field, DumbMerge):
            values = [(bit_field >> offset) & mask for (_, mask, offset) in self.name_mask_offsets]
        elif not any(isinstance(value, DumbMerge) for value in values):
            bit_field = reduce(operator.or_, (((value & mask) << offset) for (value, (_, mask, offset)) in izip(values, self.name_mask_offsets)))
        return super(BitField, self)._decipher(container, bit_field, *values)

            
