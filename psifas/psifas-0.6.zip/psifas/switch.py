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
        return self.mapping(location.context(self._fields[0].name(self, location)).value)

    def mapping(self, switch_value):
        """
        maps a switch-value to a Psifas
        """
        return NoProcess()

    def reverse_mapping_location(self, location):
        solution_value = location.context().value
        if solution_value is Bottom:
            return Bottom
        return self.reverse_mapping_abstract(solution_value)

    def reverse_mapping_abstract(self, solution_value):
        if is_abstract(solution_value):
            return Bottom
        return self.reverse_mapping(solution_value)

    def reverse_mapping(self, solution_value):
        return Bottom

    def __init__(self, *switch_field):
        assert len(switch_field) <= 1, "At most one switch-field is accepted"
        if len(switch_field) == 0:
            super(MappingSwitch, self).__init__()
            return
        switch_field, = switch_field
        if isinstance(switch_field, str):
            switch_field = Link('.../' + switch_field)
        if not isinstance(switch_field, Field):
            switch_field = UniqueField('.%s' % (self.__class__.__name__.lower(),), switch_field)
        super(MappingSwitch, self).__init__(switch_field)

    def _decipher_location(self, location, all_fields):
        if len(all_fields) < 1:
            return True
        switch_value = location.context(all_fields[0].name(self, location)).value
        location.context(all_fields[0].name(self, location)).set_value(self.reverse_mapping_location(location), location)
        return switch_value is AcceptAll or not is_abstract(switch_value)

    def _all_fields(self, location):
        return (self._fields + (Field('.$choice', self.mapping_location(location)),)), False

class Switch(MappingSwitch):
    def __init__(self, switch_psifas, mapping_dict = None, default = Bottom, **mapping_extension):
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
        
        self.default = default if ((default is Bottom) or isinstance(default, Psifas)) else Constant(default)
    
    def _explicit_replace(self, old_psifas, new_psifas):
        for key, value in self.mapping_dict.items():
            if old_psifas is value:
                self.mapping_dict[key] = new_psifas
            elif isinstance(value, Psifas):
                value.replace(old_psifas, new_psifas)

    def mapping(self, switch_value):
        return self.mapping_dict.get(switch_value,
                                     self.default if not is_abstract(switch_value)
                                     else super(Switch, self).mapping(switch_value))

    def reverse_mapping_abstract(self, solution):
        if any(not isinstance(psifas, Constant) for psifas in self.mapping_dict.itervalues()):
            return Bottom
        if isinstance(self.default, Constant) and (solution == self.default.value):
            return Bottom
        result = Bottom
        for key, psifas in self.mapping_dict.iteritems():
            if psifas.value == solution:
                if result is not Bottom:
                    # 2 maps match
                    return Bottom
                result = key
        return result


class _load_mapping_dict_metaclass(type):
    """
    Do Not Panic.
    This feature simply calls load_mapping_dict automatically after
    sub-classes of Enum are created.
    """
    def __new__(mcs, name, bases, namespace):
        enum_class = type.__new__(mcs, name, bases, namespace)
        enum_class.load_mapping_dict((key, value) for (key, value) in namespace.iteritems() if key.isupper() and not key.startswith('_'))
        return enum_class

class Enum(MappingSwitch):
    """
    Inherit from this class inorder to create your own enums.
    Overwrite enum_dict to something like dict(VALUE_A = 1, VALUE_B = 2)
    """
    __metaclass__ = _load_mapping_dict_metaclass

    constants = {}

    def __init__(self, switch_psifas):
        if isinstance(switch_psifas, str):
            switch_psifas = Link('.../' + switch_psifas)
        super(Enum, self).__init__(UniqueField('enum', switch_psifas))

    @classmethod
    def load_mapping_dict(cls, constants):
        """
        This function should also be called if enum_dict is updated after
        the class creation.
        """
        cls.constants = cls.constants.copy() # don't change he original dictionary - allows inheritence
        cls.constants.update(constants)
        
        cls.mapping_dict = dict((value, Constant(key)) for (key, value) in cls.constants.iteritems())
        
    def mapping(self, switch_value):
        if not is_abstract(switch_value):
            return self.mapping_dict[switch_value]
        return self.mapping_dict.get(switch_value, Bottom)

    def reverse_mapping(self, solution):
        return self.constants.get(solution, Bottom)

class Dynamic(MappingSwitch):
    """
    Uses a dynamically-caculated psifas-class for the chosen psifas
    """
    def __init__(self, class_psifas, *dynamic_args, **dynamic_kws):
        super(Dynamic, self).__init__(class_psifas)
        self.dynamic_args = dynamic_args
        self.dynamic_kws = dynamic_kws

    def mapping_location(self, location):
        """
        maps a location to a Psifas
        """
        class_psifas = location.context(self._fields[0].name(self, location)).value
        if is_abstract(class_psifas):
            return super(Dynamic, self).mapping_location(location)
        
        return class_psifas(*self.dynamic_args, **self.dynamic_kws)
    
    def mapping(self, class_psifas):
        if is_abstract(class_psifas):
            return super(Dynamic, self).mapping(class_psifas)
        if issubclass(class_psifas, Psifas):        
            return class_psifas(*self.dynamic_args, **self.dynamic_kws)


class Try(Psifas):
    exception = PsifasException

    def __init__(self, sub_psifas, except_psifas = Bottom, exception = None, exception_field_name = None):
        super(Try, self).__init__()
        if isinstance(except_psifas, str):
            except_psifas = CLink('.../' + except_psifas)
        elif except_psifas is Bottom:
            except_psifas = Psifas()
        elif not isinstance(except_psifas, Psifas):
            except_psifas = Constant(except_psifas)

        if exception_field_name is not None:
            sub_psifas = Struct(Field('.', sub_psifas),
                                Field(exception_field_name, Constant(None)))
            # the AcceptAll makes the struct use any other value in that field (except Bottom)
            except_psifas = Struct(Field('.', except_psifas),
                                   Field(exception_field_name, Constant(AcceptAll)))
            
        self._exception_field_name = exception_field_name # should not be changed

        self.sub_psifas = sub_psifas
        self.except_psifas = except_psifas
        
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

    def _all_fields(self, location):
        if len(location) == 0 or (location[0].try_copy != 'FAILED'):
            return (self._fields + (Field('.$try', self.sub_psifas),)), False
        return (self._fields + (Field('.$try', Psifas()), Field('.$except', self.except_psifas))), False

    def _decipher_field(self, location, field, sub_location, next_sub_location):
        if field.psifas is not self.sub_psifas:
            return super(Try, self)._decipher_field(location, field, sub_location, next_sub_location)
        
        if sub_location.try_copy is None:
            sub_location.try_copy = sub_location.top_parent().create_ghost()

        try:
            return super(Try, self)._decipher_field(location, field, sub_location, next_sub_location)
        except self.exception, exc:
            top_parent = sub_location.top_parent()
            top_parent.load_ghost(sub_location.try_copy)
            top_parent.proceed()

            sub_location.try_copy = 'FAILED'
            sub_location.proceed()

            if self._exception_field_name is not None:
                sub_location.set_context_value(exc, self._exception_field_name)
        return False # this will make the parent run another loop

def TrySequence(first_psifas, *psifas_sequence):
    if len(psifas_sequence) == 0:
        return first_psifas
    return Try(TrySequence(first_psifas, *psifas_sequence[:len(psifas_sequence)/2]),
               TrySequence(*psifas_sequence[len(psifas_sequence)/2:]))

