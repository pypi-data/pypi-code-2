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
from multifield import *

class MappingSwitch(Psifas):
    def mapping_location(self, location):
        """
        maps a location to a Psifas
        """
        return self.mapping(location.context(self._fields[0].name).value)

    def mapping(self, switch_value):
        """
        maps a switch-value to a Psifas
        """
        raise NotImplementedError

    def reverse_mapping_location(self, location):
        solution_value = location.context().value
        if solution_value is NoValue:
            return NoValue
        return self.reverse_mapping(solution_value)

    def reverse_mapping(self, solution_value):
        return NoValue

    def __init__(self, *switch_field):
        assert len(switch_field) <= 1, "At most one switch-field is accepted"
        if len(switch_field) == 0:
            super(MappingSwitch, self).__init__()
            return
        switch_field, = switch_field
        if isinstance(switch_field, str):
            switch_field = Link(switch_field)
        if not isinstance(switch_field, Field):
            switch_field = Field(self.unique('.%s' % (self.__class__.__name__.lower(),)), switch_field)
        super(MappingSwitch, self).__init__(switch_field)

    def _decipher_location(self, location):
        choice_sub_location = location.get_field(len(self._fields), '.$choice')

        if len(self._fields) > 0:
            switch_value = location.context(self._fields[0].name).value
            if switch_value is NoValue:
                switch_value = self.reverse_mapping_location(location)
                if switch_value is NoValue:
                    return
                location.context(self._fields[0].name).set_value(switch_value, location)

        mapped_psifas = self.mapping_location(location)
        if mapped_psifas is NoValue:
            # If we don't know how to parse, we'll return NoValue - and will be recalled later.
            return 
        # We trust the mapping_location function to return a Psifas object.
        # If the sub location will need the stream, it will borrow it:
        if mapped_psifas.decipher_loop(choice_sub_location):
            location.proceed()

        # from here, it looks similar to the original code.
        if not location.stream_finished:
            self._decipher_stream(location)

        if choice_sub_location.decipher_finished:
            # no need to check (NoValue not in values) - this Psifas doesn't have its own values.
            location.decipher_finished = location.payload is not None

    def _decipher_stream(self, location):
        if location.stream is not None:
            location.stream_finished = True
        if not location.subpayloads_verified:
            if len(self._fields) > 0:
                switch_payload = location[0].payload
            else:
                switch_payload = ''
            choice_sub_location = location.get_field(len(self._fields), '.$choice')
            if None not in (choice_sub_location.payload, switch_payload):
                location.set_payload(switch_payload + choice_sub_location.payload)
                location.subpayloads_verified = True

class Try(Psifas):
    exception = PsifasException

    def __init__(self, sub_psifas, except_psifas = NoValue, exception = None, exception_field_name = None):
        super(Try, self).__init__()
        if isinstance(except_psifas, str):
            except_psifas = CLink('.../' + except_psifas)
        elif except_psifas is NoValue:
            except_psifas = Psifas()
        elif not isinstance(except_psifas, Psifas):
            except_psifas = Constant(except_psifas)

        if not isinstance(sub_psifas, Psifas):
            sub_psifas = Constant(sub_psifas)

        self.sub_psifas = sub_psifas
        self.except_psifas = except_psifas
        self.exception_field_name = exception_field_name
        if exception is not None:
            self.exception = exception

    def _explicit_replace(self, old_psifas, new_psifas):
        if old_psifas is self.sub_psifas:
            self.sub_psifas = new_psifas
        else:
            self.sub_psifas.replace(old_psifas, new_psifas)
        if old_psifas is self.except_psifas:
            self.except_psifas = new_psifas
        else:
            self.except_psifas.replace(old_psifas, new_psifas)

    def _decipher_location(self, location):
        if location.try_copy is None:
            location.try_copy = location.top_parent().create_ghost()
        try_sub_location = location.get_field(len(self._fields), '.$try')
        
        if location.try_copy != 'FAILED':
            try:
                sub_psifas = self.sub_psifas
                if self.exception_field_name is not None:
                    sub_psifas = Struct(Field('.', self.sub_psifas),
                                        Field(self.exception_field_name, Constant(None)))
                if sub_psifas.decipher_loop(try_sub_location): # may throw an exception
                    location.proceed() 
                if not location.stream_finished:
                    self._decipher_stream(location)

                if try_sub_location.decipher_finished:
                    # no need to check (NoValue not in values) - this Psifas doesn't have its own values.
                    location.decipher_finished = location.payload is not None
                return
                
            except self.exception, exc:
                top_parent = location.top_parent()
                top_parent.load_ghost(location.try_copy)
                top_parent.proceed()

                try_sub_location.process = Finished

                location.try_copy = 'FAILED'
                location.try_exception = exc
                location.proceed()

        # run the except-psifas
        except_sub_location = location.get_field(len(self._fields) + 1, '.$except')
        except_psifas = self.except_psifas
        if self.exception_field_name is not None:
            except_psifas = Struct(Field('.', self.except_psifas),
                                   Field(self.exception_field_name, Constant(location.try_exception)))
        if except_psifas.decipher_loop(except_sub_location):
            location.proceed()
            
        if not location.stream_finished:
            self._decipher_stream(location)

        if except_sub_location.decipher_finished:
            # no need to check (NoValue not in values) - this Psifas doesn't have its own values.
            location.decipher_finished = location.payload is not None

    def _decipher_stream(self, location):
        if location.stream is not None:
            location.stream_finished = True
        if not location.subpayloads_verified:
            if location.try_copy != 'FAILED':
                sub_location = location.get_field(len(self._fields), '.$try')
            else:
                sub_location = location.get_field(len(self._fields) + 1, '.$except')
            if sub_location.payload is not None:
                location.set_payload(sub_location.payload)
                location.subpayloads_verified = True

def TrySequence(first_psifas, *psifas_sequence):
    if len(psifas_sequence) == 0:
        return first_psifas
    return Try(TrySequence(first_psifas, *psifas_sequence[:len(psifas_sequence)/2]),
               TrySequence(*psifas_sequence[len(psifas_sequence)/2:]))

class Switch(MappingSwitch):
    def __init__(self, switch_psifas, mapping_dict = None, default = NoValue, **mapping_extension):
        if mapping_dict is None:
            mapping_dict = dict()
        if isinstance(switch_psifas, str):
            switch_psifas = CLink(switch_psifas)
        elif not isinstance(switch_psifas, Psifas):
            switch_psifas = Constant(switch_psifas) # huh? Constant switch-field?
        
        super(Switch, self).__init__(switch_psifas)

        self.mapping_dict = dict(mapping_dict, **mapping_extension)
        for (key, value) in self.mapping_dict.items():
            if not isinstance(value, Psifas):
                self.mapping_dict[key] = Constant(value)
        
        self.default = default if ((default is NoValue) or isinstance(default, Psifas)) else Constant(default)
    
    def _explicit_replace(self, old_psifas, new_psifas):
        if old_psifas is self.switch_psifas:
            self.switch_psifas = new_psifas
        else:
            self.switch_psifas.replace(old_psifas, new_psifas)
        for key, value in self.mapping_dict.items():
            if old_psifas is value:
                self.mapping_dict[key] = new_psifas
            elif isinstance(value, Psifas):
                value.replace(old_psifas, new_psifas)

    def mapping(self, switch_value):
        return self.mapping_dict.get(switch_value, self.default)

    def reverse_mapping(self, solution):
        if any(not isinstance(psifas, Constant) for psifas in self.mapping_dict.itervalues()) or \
           ((self.default is not NoValue) and not isinstance(self.default, Constant)):
            # reverse-mapping works only for a mapping to constants.
            return NoValue
        if (self.default is not NoValue) and (solution == self.default.value):
            return NoValue
        result = NoValue
        for key, psifas in self.mapping_dict.iteritems():
            if psifas.value == solution:
                if result != NoValue:
                    # 2 maps match
                    return NoValue
                result = key
        return result

class _reload_enum_dict_metaclass(type):
    """
    Do Not Panic.
    This feature simply calls reload_enum_dict automatically after
    sub-classes of Enum are created.
    """
    def __new__(mcs, name, bases, namespace):
        enum_class = type.__new__(mcs, name, bases, namespace)
        enum_class.reload_enum_dict()
        return enum_class

class Enum(MappingSwitch):
    """
    Inherit from this class inorder to create your own enums.
    Overwrite enum_dict to something like dict(VALUE_A = 1, VALUE_B = 2)
    """
    __metaclass__ = _reload_enum_dict_metaclass

    enum_dict = {}

    def __init__(self, switch_psifas):
        if isinstance(switch_psifas, str):
            switch_psifas = Link('.../' + switch_psifas)
        super(Enum, self).__init__(Field(self.unique('enum'), switch_psifas))

    @classmethod
    def reload_enum_dict(cls):
        """
        This function should also be called if enum_dict is updated after
        the class creation.
        """
        cls.mapping_dict = dict((value, Constant(key)) for (key, value) in cls.enum_dict.iteritems())

    #No explicit replace here: the mapping_dict's psifases must match the enum_dict.

    def mapping(self, switch_value):
        return self.mapping_dict[switch_value]

    def reverse_mapping(self, solution):
        return self.enum_dict.get(solution, NoValue)

class Dynamic(MappingSwitch):
    """
    Uses a dynamically-caculated psifas-class for the chosen psifas
    """
    def __init__(self, class_psifas, *dynamic_args, **dynamic_kws):
        super(Dynamic, self).__init__(class_psifas)
        self.dynamic_args = dynamic_args
        self.dynamic_kws = dynamic_kws

    def mapping(self, class_psifas):
        if issubclass(class_psifas, Psifas):
            return class_psifas(*self.dynamic_args, **self.dynamic_kws)
