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

from itertools import izip
from copy import deepcopy
from utils import *
from psifas_exceptions import *
from imerge import imerge
from datatypes.dummy import DummyPayload, BottomTuple
from datatypes.pretty import Pretty
from datatypes.container import Container

import operator

class Field(object):
    __slots__ = ['_full_name', '_name', 'psifas']
    def __init__(self, full_name, psifas):
        super(Field, self).__init__()
        # assert '/' not in full_name
        # assert name not in ('', '.', '..', '...')
        if not isinstance(psifas, Psifas):
            psifas = Constant(psifas)
            
        self._full_name = full_name
        self._name = full_name.split('$', 1)[0]
        self.psifas = psifas

    def name(self, creator, location):
        return self._name

    def full_name(self, creator, location):
        return self._full_name

class UniqueField(Field):
    def name(self, creator, location):
        return "%s#%s%d" % (self._name, creator.__class__.__name__, id(location))

    def full_name(self, creator, location):
        return "%s#%s%d" % (self._full_name, creator.__class__.__name__, id(location))
    

class Psifas(Pretty):
    DEEP_DEBUG_MODE = True

    spiritual = False
    
    def __init__(self, *fields, **kw):
        self._fields = fields
        self.spiritual = kw.pop('spiritual', self.spiritual)

        super(Psifas, self).__init__(**kw)

    @recursion_lock(lambda self, sub_psifas, new_sub_psifas: None)
    def replace(self, sub_psifas, new_sub_psifas):
        """
        Recursively replace one Psifas with a different Psifas
        """
        for field in self._fields:
            if field.psifas is sub_psifas:
                field.psifas = new_sub_psifas
            else:
                field.psifas.replace(sub_psifas, new_sub_psifas)
        self._explicit_replace(sub_psifas, new_sub_psifas)

    def _explicit_replace(self, old_psifas, new_psifas):
        """
        override this if there are other psifases to search and replace
        """
        pass

    def _decipher_location_set(self, location, all_fields):
        values = tuple(self._decipher_values(location, all_fields))

        location.set_context_value(values[0])
        for field, value in izip(all_fields, values[1:]):
            location.set_context_value(value, field.name(self, location))

        return values

    def _decipher_location(self, location, all_fields):
        """
        Builds this psifas's value and the sub-fields' values (if not built).
        
        Returns True iff deciphering finished
        """
        self._decipher_location_set(location, all_fields)
        return True
    
    def _decipher_values(self, location, all_fields):
        """
        Should return the values of the field and its sub-fields.
        By default, executes the _decipher function that only receives
        the fields' values, without the location object.
        """
        return self._decipher(location, location.context().value, *(location.context(field.name(self, location)).value for field in all_fields))
        
    def _decipher(self, location, value, *sub_values):
        """
        Should try to complete the missing values - those with Bottom.
        """
        if Bottom not in sub_values:
            parse_value = self._parse(*sub_values)
            return (parse_value,) + sub_values
        return (value,) + sub_values

    def _parse(self, *values):
        """
        Called when all sub-fields have values (not Bottom).
        By default, this returns AcceptAll, which means that this
        psifas finished its calculations.
        """
        return AcceptAll

    def decipher_loop(self, location):
        process = location.process
        try:
            self._decipher_loop(location)
        except MergeException, e:
            raise Contradiction("in %s: %r" % (location, e))
        except DecipherException, e:
            raise
        except Exception, e:
            if self.DEEP_DEBUG_MODE:
                raise # this will raise the exception as-is, so exact traceback can be made.
            raise DecipherException('Deciphering failed at %s' % (location,), e)            
        return location.process != process
    
    def _all_fields(self, location):
        return self._fields, False

    def _decipher_field(self, location, field, sub_location, next_sub_location):
        """
        This code was moved from the _decipher_loop for-loop,
        so the for-loop could be called twice without code duplication.
        """
        payload_offset_fixed = operator.isNumberType(sub_location.payload_offset)
        if payload_offset_fixed and not is_abstract(sub_location.payload) and next_sub_location is not None:
            next_sub_location.set_payload_offset(sub_location.payload_offset + len(sub_location.payload))
        
        if sub_location.process is Finished:
            return True
            
        if not sub_location.payload_deciphered:
            next_payload_offset_fixed = next_sub_location is not None and operator.isNumberType(next_sub_location.payload_offset)
            if payload_offset_fixed:
                if next_payload_offset_fixed:
                    sub_payload_slice = abstract_slice(location.payload, sub_location.payload_offset, next_sub_location.payload_offset)
                    sub_location.set_payload(sub_payload_slice)
                    # if the slice is concrete, there's no need to repeat on this code
                    # TODO: think of other cases where it is useless to repeat this code
                else:
                    sub_location.set_payload(prefix_from_offset(location.payload, sub_location.payload_offset))
                    if next_sub_location is not None:
                        # maybe we can evaluate the next payload offset
                        if is_sequence_type(sub_location.payload):
                            next_sub_location.set_payload_offset(sub_location.payload_offset + len(sub_location.payload))
                        elif isinstance(sub_location.payload, Prefix) and sub_location.payload.is_hole_string():
                            next_sub_location.set_payload_offset(sub_location.payload_offset + sub_location.payload.min_length)
                # we know a slice of our payload:
                if sub_location.payload == '':
                    if sub_location.payload_offset > 0:
                        location.set_payload(Prefix(SparseString(), min_length = sub_location.payload_offset))
                elif not is_abstract(location.payload):
                    if not is_abstract(sub_location.payload):
                        location.imerge(location.payload[sub_location.payload_offset:sub_location.payload_offset + len(sub_location.payload)],
                                        sub_location.payload)
                    else:
                        location.imerge(location.payload[sub_location.payload_offset:], sub_location.payload + SparseString())
                else:
                    # This is the general case. For efficiency, we try the cases above.
                    location.set_payload(HoleString(BottomTuple(sub_location.payload_offset)) +
                                         sub_location.payload + SparseString())
                if not is_abstract(sub_location.payload):
                    sub_location.payload_deciphered = True
            else:
                if next_payload_offset_fixed:
                    # we don't have an implementation to represent Suffixes
                    # we know the maximal size...
                    sub_location.set_payload(Prefix(BottomTuple(next_sub_location.payload_offset)))
                    if is_sequence_type(sub_location.payload):
                        sub_location.set_payload_offset(next_sub_location.payload_offset - len(sub_location.payload))
                        # TODO: raise exception if the new offset is negative?
        
        if field.psifas.decipher_loop(sub_location):
            location.proceed()

        return sub_location.process is Finished

    def _decipher_loop(self, location):
        """
        This is the heart of the Psifas algorithm.
        It loops over the sub-fields and the current field and
        tries to 'decipher' them. It will stop when all decipherings
        finished, or when none called 'proceed()' for a full loop.
        """
        # the process may not be 0 on the first loop: for example if parent location called
        # set_payload_offset
        if self.spiritual:
            location.context().spiritual = True

        process = None
        while process != location.process:
            # loops until there are no changes
            process = location.process

            all_fields, any_more_fields = self._all_fields(location)
            location.create_sublocations(self, all_fields)

            all_locations_deciphered = all_fields_finished = not any_more_fields
            if len(all_fields) > 0:
                location[0].set_payload_offset(0)
                
                for (field, (sub_location, next_sub_location)) in izip(all_fields, pairwise_longest(location)):
                    if not self._decipher_field(location, field, sub_location, next_sub_location):
                        all_fields_finished = False
                        if not sub_location.location_deciphered:
                            all_locations_deciphered = False
                
                # sub_location is the last sub-location
                if not any_more_fields and operator.isNumberType(sub_location.payload_offset):
                    # fixes the payload's length
                    # TODO: think about a new attr last_subpayload_deciphered to avoid repeating this code:
                    sub_payload_slice = abstract_slice(location.payload, sub_location.payload_offset, None)
                    sub_location.set_payload(sub_payload_slice)
                    
                    private_payload = self._private_payload(location, all_fields)
                    
                    location.set_payload(HoleString(BottomTuple(sub_location.payload_offset)) +
                                         sub_location.payload + private_payload)
            else:
                location.set_payload(self._private_payload(location, all_fields))
                    
            if not location.location_deciphered:
                # marks location_decipher if the payload and all the relevant values have
                # been calculated.
                if self._decipher_location(location, all_fields):
                    location.location_deciphered = all_locations_deciphered
                
            if all_fields_finished and location.location_deciphered and location.payload_deciphered:
                location.process = Finished
                break
            
    def _private_payload(self, location, all_fields):
        return ''
    
    def _create_top_location_from_payload(self, payload, ignore_leftover):
        if not isinstance(payload, str):
            # it is a stream
            payload = Prefix(DummyPayload(payload))
        elif ignore_leftover:
            payload = Prefix(payload)
        
        return TopLocation(payload)

    def parse(self, payload, ignore_leftover = False):
        location = self._create_top_location_from_payload(payload, ignore_leftover)
        self._validated_parse(location)
        return location.context().value
    
    def parse_debug(self, payload, ignore_leftover = False):
        location = self._create_top_location_from_payload(payload, ignore_leftover)
        try:
            self._validated_parse(location)
        except PsifasException, e:
            return location, e
        return location, None

    def build(self, value, allow_sparse = False):
        location = TopLocation()
        location.context().value = value
        self._validated_build(location, allow_sparse)
        return location.payload

    def build_debug(self, context, allow_sparse = False):
        location = TopLocation()
        location._context = context
        try:
            self._validated_build(location, allow_sparse)
        except PsifasException, e:
            return location, e
        return location, None

    def complete(self, value):
        """
        builds the value, but returns the context's value.
        Usefull when only the auto-complete features are required.
        """
        location = TopLocation()
        location.context().value = value
        self._decipher_debug(location)
        return location.context().value
    
    def _decipher_debug(self, top_location):
        while top_location.process is not Finished:
            if not self.decipher_loop(top_location):
                break

    def _validated_build(self, top_location, allow_sparse = False):
        self._decipher_debug(top_location)
        if not allow_sparse and is_abstract(top_location.payload):
            raise DecipherException("deciphering did not finish due to missing dependencies: \n%s" % (top_location.context().tree(),))

    def _validated_parse(self, top_location):
        self._decipher_debug(top_location)
        if top_location.context().value is Bottom:
            raise DecipherException("deciphering did not finish due to missing dependencies: \n%s" % (top_location.context().tree(),))
        
    def __sub__(self, other):
        return self + (-other)
    
    def on(self, *args, **kw):
        return On(self, *args, **kw)

    def struct(self):
        import multifield
        return multifield.Struct('.', self)

class ConcretePsifas(Psifas):
    def _decipher_values(self, location, all_fields):
        """
        filters the values - all dumb values are replaced with Bottom
        """
        values = [location.context().value] + [location.context(field.name(self, location)).value for field in all_fields]
        return self._decipher(location, *(Bottom if is_abstract(value) else value for value in values))
    

class Constant(Psifas):
    def __new__(cls, value):
        if isinstance(value, Link):
            return ConstantLink(value)
        return super(Constant, cls).__new__(cls)
    
    def __init__(self, value):
        super(Constant, self).__init__()
        self.value = value

    def _decipher_location(self, location, all_fields):
        self._decipher_location_set(location, all_fields)
        return True
    
    def _parse(self):
        return self.value

class ConstantLink(Psifas):
    def __init__(self, value):
        super(ConstantLink, self).__init__()
        # assert isinstance(value, Link)
        self.value = value

    def _decipher_location(self, location, all_fields):
        self._decipher_location_set(location, all_fields)
        return not is_abstract(location.context('').value)
    
    def _parse(self):
        return self.value

class CLink(ConstantLink):
    def __init__(self, target = '.'):
        super(CLink, self).__init__(Link(target))

    def __getitem__(self, key):
        return CLink(self.value.join(Path(key)).to_string())

    def __getattr__(self, key):
        return self.__getitem__(key)

This = CLink('...')

class CLinkContainer(CLink):
    def _decipher_location(self, location, all_fields):
        value, = self._decipher_location_set(location, all_fields)
        if isinstance(value, Link):
            pointed_value = location.context('').value
            return isinstance(pointed_value, Container) or not is_abstract(pointed_value)
        return True

class NoProcess(Psifas):
    def __init__(self):
        super(NoProcess, self).__init__()

    def _decipher_loop(self, location):
        return

class FixedSizeSegment(Psifas):
    def __init__(self, size):
        super(FixedSizeSegment, self).__init__()
        self.size = size

    def _private_payload(self, location, all_fields):
        return location.imerge(location.context().value, HoleString(BottomTuple(self.size)))

    def _decipher_values(self, location, all_fields):
        return (location.payload,)

    def _decipher_location(self, location, all_fields):
        payload, = self._decipher_location_set(location, all_fields)
        return not is_abstract(payload)

class Segment(Psifas):
    def __new__(cls, sizer):
        if operator.isNumberType(sizer):
            return FixedSizeSegment(sizer)
        return super(Segment, cls).__new__(cls)

    def __deepcopy__(self, memo):
        instance = memo.get(self, None)
        if instance is not None:
            return instance
        memo[self] = instance = super(Segment, self).__new__(self.__class__)
        instance.__dict__.update(deepcopy(self.__dict__, memo))
        return instance
        
    def __init__(self, sizer):
        if isinstance(sizer, str):
            sizer = Link('.../' + sizer)
        super(Segment, self).__init__(UniqueField('size', sizer))

        self._extra_noprocess_field = Field('.', NoProcess())

    def _all_fields(self, location):
        size = location.context(self._fields[0].name(self, location)).value
        if is_abstract(size):
            return (self._fields + (self._extra_noprocess_field,)), False
        return (self._fields + (Field('.', FixedSizeSegment(size)),)), False

    def _decipher(self, location, value, size, payload):
        payload = location.imerge(payload, value)
        if is_sequence_type(payload):
            try:
                size = location.imerge(size, len(payload))
            except MergeException:
                raise MergeException("Segment's payload is not in the length of its required size", size, len(payload))
        elif not is_abstract(size):
            payload = location.imerge(payload, Prefix(BottomTuple(size), size))
        return (payload, size, payload)
        
class Leftover(Psifas):
    def __init__(self):
        super(Leftover, self).__init__()

    def _private_payload(self, location, all_fields):
        return location.context().value

    def _decipher_values(self, location, all_fields):
        return (location.payload,)
        
class IsEOF(Psifas):
    def __init__(self):
        super(IsEOF, self).__init__()
        
    def _decipher_location(self, location, all_fields):
        up_location = location
        while up_location.payload_offset is not None:
            if is_abstract(up_location.payload_offset):
                # we don't know if we're in EOF
                break
            if is_abstract(up_location.payload) or is_abstract(up_location.parent.payload):
                # we don't know if we're in EOF
                break
            # TODO: what about DummyPayload?
            if up_location.payload_offset + len(up_location.payload) != len(up_location.parent.payload):
                # not EOF
                location.set_context_value(False)
                return True
            up_location = up_location.parent
        else:
            location.set_context_value(True)
            return True
        return False

class On(Psifas):
    def __init__(self, sub_psifas, target, leftover_field_name = None):
        import multifield
        if isinstance(target, str):
            target = Link(target)
            
        super(On, self).__init__(UniqueField('.on', target))
        
        if leftover_field_name is not None:
            sub_psifas = multifield.Struct(Field('.', sub_psifas),
                                           Field(leftover_field_name, Leftover()))
        self.sub_psifas = sub_psifas
        
    def _explicit_replace(self, old_psifas, new_psifas):
        if old_psifas is self.sub_psifas:
            self.sub_psifas = new_psifas
        else:
            self.sub_psifas.replace(old_psifas, new_psifas)

    def _decipher_location(self, location, all_fields):
        location_deciphered = super(On, self)._decipher_location(location, all_fields)
        
        sub_location = location.get_field(len(all_fields))
        
        on_data = location.context(all_fields[0].name(self, location)).value
        sub_location.set_payload(on_data)
        
        # just like we do for normal fields (without setting the payload_offset)
        if sub_location.process is not Finished:
            if self.sub_psifas.decipher_loop(sub_location):
                location.proceed()
                
        location.set_context_value(sub_location.payload, all_fields[0].name(self, location))
        
        return location_deciphered and (sub_location.process is Finished)

class Copy(Psifas):
    def __init__(self, copyof):
        if isinstance(copyof, str):
            copyof = Link('.../' + copyof)
        super(Copy, self).__init__(UniqueField('.copy', copyof))

    def _get_copy(self):
        return self._fields[0].psifas

    def _set_copy(self, new_psifas):
        self._fields[0].psifas = new_psifas

    copy = property(_get_copy, _set_copy)

    def _decipher(self, location, value, copyof):
        value = location.imerge(value, copyof)
        return (value, value)
                
            
            
