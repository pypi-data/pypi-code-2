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
from utils import *
from psifas_exceptions import *

DEEP_DEBUG_MODE = False

class Field(object):
    __slots__ = ['full_name', 'name', 'psifas']
    def __init__(self, full_name, psifas):
        super(Field, self).__init__()
        # assert '/' not in full_name
        # assert name not in ('', '.', '..', '...')
        if not isinstance(psifas, Psifas):
            psifas = Constant(psifas)

        self.full_name = full_name
        self.name = full_name.split('$', 1)[0]
        self.psifas = psifas

class Psifas(object):
    spiritual = False

    def __init__(self, *fields, **kw):
        self._fields = fields
        self.spiritual = kw.pop('spiritual', self.spiritual)

        super(Psifas, self).__init__(**kw)

    def unique(self, s):
        return '%s#%d' % (s, id(self))

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

    def _decipher_location(self, location):
        """
        Builds the payload by calling _decipher_stream,
        Builds this psifas's value and the sub-fields' values (if not built).

        Returns True iff deciphering finished
        """
        if not location.stream_finished:
            self._decipher_stream(location)
        values = tuple(self._decipher_values(location))

        location.context().set_value(values[0], location)
        for field, value in izip(self._fields, values[1:]):
            location.context(field.name).set_value(value, location)
        location.decipher_finished = (location.payload is not None) and (NoValue not in values)

    def _join_subpayloads(self, location):
        sub_payloads = []
        for sub_location in location.iter_fields(self._fields):
            sub_payload = sub_location.payload
            if sub_payload is None:
                return None
            sub_payloads.append(sub_payload)
        return ''.join(sub_payloads)

    def _decipher_stream(self, location):
        """
        Builds the payload.
        By default, the psifas object does not need to read from the stream,
        and the payload is equal to the concatination of the sub-fields'
        payloads.
        """
        if location.stream is not None:
            location.stream_finished = True
        if not location.subpayloads_verified:
            # if subpayloads_verified is True, there's no point in setting the payload again
            total_payload = self._join_subpayloads(location)
            if total_payload is not None:
                location.set_payload(total_payload)
                location.subpayloads_verified = True
    
    def _decipher_values(self, location):
        """
        Should return the values of the field and its sub-fields.
        By default, executes the _decipher function that only receives
        the fields' values, without the location object.
        """
        return self._decipher(location.context().value, *[location.context(field.name).value for field in self._fields])

    def _decipher(self, value, *sub_values):
        """
        Should try to complete the missing values - those with NoValue.
        """
        if NoValue not in sub_values:
            parse_value = self._parse(*sub_values)
            return (parse_value,) + sub_values
        return (value,) + sub_values

    def _parse(self, *values):
        """
        Called when all sub-fields have values (not NoValue).
        By default, this returns AcceptAll, which means that this
        psifas finished its calculations.
        """
        return AcceptAll

    def decipher_loop(self, location):
        process = location.process
        try:
            self._decipher_loop(location)
        except DecipherException, e:
            raise
        except Exception, e:
            if DEEP_DEBUG_MODE:
                raise # this will raise the exception as-is, so exact traceback can be made.
            raise DecipherException('Deciphering failed at %s' % (location,), e)            
        return location.process != process
    
    def _decipher_loop(self, location):
        """
        This is the heart of the Psifas algorithm.
        It loops over the sub-fields and the current field and
        tries to 'decipher' them. It will stop when all decipherings
        finished, or when none called 'proceed()' for a full loop.
        """
        if self.spiritual and (0 == location.process):
            location.context().spiritual = True
            
        if location.parent_stream() is not None:
            # the parent holds a stream.
            if location.payload is not None and not location.parent_stream_used:
                # verify payload against parent's stream
                real_payload = location.parent.stream.read(len(location.payload), best_effort = True)
                if real_payload != location.payload:
                    raise Contradiction("Expected payload doesn't match real payload", location.payload, real_payload)
                location.parent_stream_used = True
                location.proceed()
            if location.process is Finished:
                # location.payload is not None and all sub fields deciphering finished -
                # nothing to do anymore.
                return
            if location.stream is None and not location.stream_finished:
                # we never worked with a stream - let's borrow from parent
                location.stream = location.parent.stream
                location.parent_stream_borrowed = True
                location.parent_stream_used = True
                location.parent.stream = None
                location.proceed()
        elif location.stream is None and not location.stream_finished and location.payload is not None:
            # we don't have a stream, neither the parent.
            # but we can use the payload as our stream.
            location.stream = PsifasStream(location.payload)
            location.proceed()

        process = None
        while process != location.process:
            # loops until there are no changes
            process = location.process
            all_fields_finished = True
            for field, sub_location in izip(self._fields, location.iter_fields(self._fields)):
                if sub_location.process is Finished:
                    continue
                if field.psifas.decipher_loop(sub_location):
                    location.proceed()

                if sub_location.process is not Finished:
                    all_fields_finished = False # not all sub-fields finished
                        
            # Now we will start handling this field.
            if not location.decipher_finished:
                # This function is expected to mark decipher_finished if the
                # payload and all the relevant values have been calculated.
                # It is also expected to mark stream_finished if the stream
                # was fully used.
                self._decipher_location(location)
                
            if all_fields_finished and location.decipher_finished:
                location.process = Finished
                break
            
        # finished using the stream - we should nullify location.stream
        if location.stream_finished and (location.stream is not None):
            if location.parent_stream_borrowed:
                # return the stream to parent
                location.parent.stream = location.stream
            else:
                # the stream was created from the payload
                if location.stream.tell() != len(location.payload):
                    raise Contradiction("Not all the payload was used" % (location.payload, location.stream))
            location.stream = None
            location.proceed()
                        
    def parse(self, stream):
        location = TopLocation(stream)
        self._decipher_debug(location)
        return location.context().value

    def parse_debug(self, stream):
        location = TopLocation(stream)
        try:
            self._decipher_debug(location)
        except PsifasException, e:
            return location, e
        return location, None

    def build(self, value):
        location = TopLocation()
        location.context().value = value
        self._decipher_debug(location)
        return location.payload

    def build_debug(self, context):
        location = TopLocation()
        location._context = context
        try:
            self._decipher_debug(location)
        except PsifasException, e:
            return location, e
        return location, None

    def _decipher_debug(self, top_location):
        while self.decipher_loop(top_location):
            pass
        if top_location.process is not Finished:
            raise DecipherException("deciphering did not finish due to missing dependencies: \n%s" % (top_location.context().tree(),))

    def __sub__(self, other):
        return self + (-other)

    def on(self, *args, **kw):
        return On(self, *args, **kw)

    def struct(self):
        import multifield
        return multifield.Struct('.', self)

class Constant(Psifas):
    def __init__(self, value):
        super(Constant, self).__init__()
        self.value = value

    def _parse(self):
        return self.value

class CLink(Constant):
    def __init__(self, link = '.'):
        super(CLink, self).__init__(Link(link))

    def __getitem__(self, key):
        return CLink(self.value.join(Path(key)).to_string())

    def __getattr__(self, key):
        return self.__getitem__(key)

This = CLink('...')

class _NeverFinish(Psifas):
    def _parse(self, *sub_values):
        return NoValue

class _NeverFinishHoldStream(_NeverFinish):
    def _decipher_stream(self, location):
        return

class Segment(Psifas):
    def __init__(self, sizer):
        if isinstance(sizer, str):
            sizer = Link('.../' + sizer)
        super(Segment, self).__init__(Field('size', sizer))

    def _decipher_stream(self, location):
        sizer_payload = location[0].payload
        if sizer_payload is None:
            return

        if location.stream is not None:
            size = location.context(self._fields[0].name).value
            if size is not NoValue:
                location.set_payload(sizer_payload + location.stream.read(size))
                location.stream_finished = True
                location.subpayloads_verified = True
                
        if not location.subpayloads_verified:
            value = location.context().value
            if value is not NoValue:
                location.set_payload(sizer_payload + value)
                location.subpayloads_verified = True

    def _decipher_values(self, location):
        sizer_payload = location[0].payload

        if None not in (sizer_payload, location.payload):
            segment = location.payload[len(sizer_payload):]
            return (segment, len(segment))
        else:
            segment = location.context().value
            if segment is not NoValue:
                return (segment, len(segment))
        return (NoValue, NoValue)
        
class Leftover(Psifas):
    def __init__(self):
        super(Leftover, self).__init__(Field('size', Psifas()))
        
    def _decipher_stream(self, location):
        if location.stream is not None:
            location.set_payload(location.stream.read_all())
            location.stream_finished = True
            location.subpayloads_verified = True
        if not location.subpayloads_verified:            
            value = location.context().value
            if value is not NoValue:
                location.set_payload(value)
                location.subpayloads_verified = True

    def _decipher_values(self, location):
        if location.payload is not None:
            return (location.payload, len(location.payload))
        return (location.context().value, NoValue)

class IsEOF(Psifas):
    """
    IsEOF works only with a given stream (in parsing).
    On building, deciphering will not finish (missing dependencies).
    """
    def __init__(self):
        super(IsEOF, self).__init__()

    def _decipher_stream(self, location):
        if location.stream is not None:
            location.set_payload('')
            location.stream_finished = True
            location.subpayloads_verified = True
            location.context().set_value(location.stream.is_eof(), location)
    
class WeakIsEOF(IsEOF):
    """
    If someone else put any value in its context - the test will be skipped.
    """
    def _decipher_stream(self, location):
        super(WeakIsEOF, self)._decipher_stream(location)
        if not location.subpayloads_verified and location.context().value is not NoValue:
            location.set_payload('')
            location.subpayloads_verified = True
            

class On(Psifas):
    def __init__(self, sub_psifas, target, leftover_field_name = None):
        import multifield
        if isinstance(target, str):
            target = Link(target)

        super(On, self).__init__(Field(self.unique('.on'), target))

        if leftover_field_name is not None:
            sub_psifas = multifield.Struct(Field('.',sub_psifas),
                                           Field(leftover_field_name, Leftover()))
        self.sub_psifas = sub_psifas

    def _explicit_replace(self, old_psifas, new_psifas):
        if old_psifas is self.sub_psifas:
            self.sub_psifas = new_psifas
        else:
            self.sub_psifas.replace(old_psifas, new_psifas)

    def _decipher_values(self, location):
        sub_location = location.get_field(len(self._fields))
        on_data = location.context(self._fields[0].name).value
        if on_data is not NoValue:
            sub_location.set_payload(on_data)
        # For the sub-execution, we will nullify location.stream.
        # This way, the sub-psifas won't try to borrow it from us.
        backup_stream = location.stream
        location.stream = None
        if self.sub_psifas.decipher_loop(sub_location):
            location.proceed()
        location.stream = backup_stream

        sub_payload = sub_location.payload
                
        return (location.context().value if sub_location.process is Finished else NoValue,
                sub_payload if sub_payload is not None else NoValue)

class Copy(Psifas):
    def __init__(self, copyof):
        if isinstance(copyof, str):
            copyof = Link('.../' + copyof)
        super(Copy, self).__init__(Field(self.unique('.copy'), copyof))

    def _get_copy(self):
        return self._fields[0].psifas

    def _set_copy(self, new_psifas):
        self._fields[0].psifas = new_psifas

    copy = property(_get_copy, _set_copy)

    def _decipher(self, value, copyof):
        if copyof is not NoValue:
            return (copyof, copyof)
        elif value is not NoValue:
            return (value, value)
        return (NoValue, NoValue)
                
            
            
