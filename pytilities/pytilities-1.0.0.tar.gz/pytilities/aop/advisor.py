# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>
# 
# This file is part of pytilities.
# 
# pytilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pytilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pytilities.  If not, see <http://www.gnu.org/licenses/>.
#

__docformat__ = 'reStructuredText'

import logging
from collections import defaultdict
from inspect import isclass
from itertools import chain

from pytilities.functions import get_attr_value
from . import commands

_logger = logging.getLogger('pytilities.aop.advisor')

class Advisor(object):

    '''
    Something that can advise objects, also manages all aspects.

    Advice can be given to any non-builtin object. Advice is called before
    calling the original function/descriptor; it can modify return value,
    arguments, call the original function, or not, ... See the user guide 
    on how to write advice functions.

    There are two types of advice to be given:
    
    - class advice
    - instance advice

    Class advice is advice given to class objects. It is executed for both
    classes and instances of those classes.

    Instance advice is advice given to instance objects. It is executed only
    for instances.

    Instance advice always wraps class advice; i.e. upon call, instance advice
    is processed first.

    A special kind of advice exists that allows you to advise any member
    of a class. This advice is called * advice, it exists for class and
    instance advice. It requires the advised object has AOPMeta as its
    metaclass. You can give * advice by specifying '*' as the member
    to advise.

    No advice, not even * advice, can advice private/protected members. Members are
    considered private/protected if their name begins with a single '_', but
    isn't special. You can, however, advice some special attributes that are
    not in advisor.unadvisables.

    Advice can be given separately to gets, sets, dels and calls of a member.
    Call advice is applied to any function returned by a get of the member it
    was given to. Note that the returned function needn't even be actual part
    of the object's dict.

    Advice is given with aspects. An aspect is a collection of advice to member
    mappings, it can be (un)applied to an object. The order in which aspects
    are applied to an object is important. Aspects last applied to an object
    will have their advice called first. Think of it as wrapping all previous
    advice with new advice. In fact, you'd best not even care about previously
    given advice. If previous advice doesn't break the interface, information
    is hidden well enough not to think about other advice, and by doing so
    reduce coupling.

    Note on static methods: with a class A, an instance a and a static method
    h; A.h() is not necessarily the same as a.h() as a.h() might be given
    instance advice. (this may be non-intuitive, but the converse was near
    impossible to implement)
    '''

    def __init__(self):
        self.__implicits = set('''
            __add__ __sub__ __mul__ __truediv__ __floordiv__ __mod__ 
            __divmod__ __pow__ __lshift__ __rshift__ __and__ __xor__ __or__
            __radd__ __rsub__ __rmul__ __rtruediv__ __rfloordiv__ 
            __rmod__ __rdivmod__ __rpow__ __rlshift__ __rrshift__ __rand__ 
            __rxor__ __ror__
            __iadd__ __isub__ __imul__ __itruediv__ __ifloordiv__ 
            __imod__ __idivmod__ __ipow__ __ilshift__ __irshift__ __iand__ 
            __ixor__ __ior__
            __neg__ __pos__ __abs__ __invert__
            __complex__ __int__ __float__ __round__
            __index__
            __len__ __getitem__ __setitem__ __delitem__ __iter__ __reversed__ 
            __contains__
            __del__ __repr__ __str__ __format__ __lt__ __le__ __eq__ __ne__
            __gt__ __ge__ __bool__'''.split())
        '''set of attribute names that are looked up directly on the class
        dict, without even calling meta *attr'''

        self.__advised_objects = defaultdict(list)
        '''{obj: [aspect, ...]} with left being the most inner aspect'''

        self.unadvisables = {'__class__', '__dict__', '__mro__', '__call__', 
                               '__closure__', '__code__', '__globals__', 
                               '__self__', '__hash__', '__doc__'}
        '''Names of attributes that cannot be advised'''

    def is_advisable(self, name):
        '''
        See if an attribute with name `name` is advisable.
        '''
        # some special attribs are unadvisable
        # no priv/protected attrib is advisable
        return not (name in self.unadvisables or 
                (name.startswith('_') and not name.startswith('__')))

    def unapply_all(self, obj):
        '''
        Unapply all advice given to an object.

        aspect.unapply(obj) is called for any aspect applied to this object.
        You should call this from your advised object's dtor or del handler.

        :param obj: the object to advise
        :type obj: class or instance
        '''
        return obj in self.__advised_objects and \
               aspect in self.__advised_objects[obj]

    def is_applied(self, aspect, obj):
        '''
        Get if this aspect is currently applied to an object.

        Note to user: use aspect.is_applied(obj) instead

        :param obj: the object to advise
        :type obj: class or instance
        :return: True if advice is currently applied to `obj`, False otherwise
        '''
        return obj in self.__advised_objects and \
               aspect in self.__advised_objects[obj]

    def apply(self, aspect, obj, members):
        '''
        Apply an aspect to an object.

        If the aspect was already applied, this call does nothing.
        
        Note to user: use aspect.apply(obj) instead

        :param aspect: the aspect to apply
        :type aspect: `Aspect`
        :param obj: the object to advise
        :type obj: class or instance
        :param members: members that are advised by the aspect
        :type members: set of str
        '''
        assert not (members & self.unadvisables), \
                '%s are unadvisable' % (members & self.unadvisables)

        if not self.is_applied(aspect, obj):
            # if is aopmeta capable:
            if isinstance(obj.__class__, AOPMeta) or isinstance(obj, AOPMeta):
                # supports implicits, regular and * advice
                # place descs on implicits
                if '*' in members:
                    place_members = self.__implicits
                else:
                    place_members = members & self.__implicits

                self.__place_descriptors(obj, place_members)
            else:
                assert '*' not in members, \
                        '* advice not supported on non AOPMeta objects'

                # place descs on every member
                self.__place_descriptors(obj, members)

            # now activate the new advice (activating late prevents errors with
            # advice that fiddles with setters)
            self.__advised_objects[obj].append(aspect)

    def __place_descriptors(self, obj, members):
        '''places aop descriptors on given members of obj'''
        if not isclass(obj): # be sure to put them on a class, not an instance
            obj = obj.__class__

        for member in members:
            try:
                value = get_attr_value(obj, member)
            except AttributeError:
                value = None

            if not (value and isinstance(value, _AOPDescriptor)):
                setattr(obj, member, _AOPDescriptor(value, member))

    def unapply(self, aspect, obj):
        '''
        Unapply an aspect of an object.

        If the aspect wasn't applied, do nothing.

        Note to user: use aspect.unapply(obj) instead

        :param aspect: the aspect to apply
        :type aspect: `Aspect`
        :param obj: the object to advise
        :type obj: class or instance
        '''
        if self.is_applied(aspect, obj):
            self.__advised_objects[obj].remove(aspect)

    def __get_advice(self, obj, member, access):
        '''
        Get iter of advice for `member` of `obj`.

        :param obj: the object to advise
        :type obj: class or instance
        :param member: member of the object
        :type member: _AOPDescriptor
        :param access: the type of access being done
        :type access: '__get__', '__set__', '__delete__' or '__call__'
        :return: advice funcs, the left is the most outer advice (i.e. the
            first advice to call, the last advice given, with class advice
            preceding instance advice)
        :rtype: iter(advice...)
        '''
        iterators = []

        if obj in self.__advised_objects:
            for aspect in reversed(self.__advised_objects[obj]):
                iterators.append(aspect.get_advice(member, access))

        if not isclass(obj):
            iterators.append(self.__get_advice(obj.__class__, member, access))
            
        return chain(*iterators)

    def process_call(self, obj, member, advised, access, args, kwargs):
        '''
        Process a get/set/del/regular call to an attribute.

        Class and instance advice will be applied to the call.

        Internal function.

        :param obj: the object to advise
        :type obj: class, instance
        :param member: member name of the object
        :type member: str
        :param access: the type of access being done
        :type access: '__get__', '__set__', '__delete__' or '__call__'
        :param args: positional args of the call. Must include the self param,
            if any
        :param kwargs: keyword args of the call
        :param function: when access is __call__, this function will be used as
            the advised object to call on most inner proceed.
        :return: the value that should be returned to the caller
        '''
        advices = tuple(self.__get_advice(obj, member, access))
        return self.__proceed(obj, member, advised, access, advices, 0, args, kwargs)

    def __proceed(self, obj, member, advised, access, advices, index, args, kwargs):
        '''
        advised: the function that's being advised, will be called on proceed
        access: type of access required: get, set, del, call
        advices: list of advice: [[advice, generator], ...]
        index: currend advice in advices
        args: a list of positional args
        kwargs: a dictionary of keyword args
        '''
        # Note: welcome to procedural land of recursion!
        if index == len(advices): # no more advice, call advised
            return advised(*args, **kwargs)

        # fetch generator
        generator = advices[index][0]()
        send_params = None
        retval = None

        while True:
            # grab next command
            try:
                command = generator.send(send_params)
            except StopIteration:
                # gen died, ret value
                advices[index][1] = None
                return retval

            # reset params, and analyse command
            send_params = None
            is_instance = not isclass(command)

            if not is_instance:
                cls = command
            else:
                cls = command.__class__

            # proceed command
            if cls is commands.proceed: # execute next level (advice or adviced)
                if is_instance:
                    assert (
                        access == '__call__' 
                        or
                        (not command.kwargs 
                         and (access == '__set__' and len(command.args) == 2)
                              or len(command.args) == 1)), (
                        'Unexpected amount of args: yield proceed(%s, %s)'
                        % (command.args, command.kwargs))

                    retval = self.__proceed(obj, member, advised, access, advices, 
                                            index+1, command.args, command.kwargs)
                else:
                    retval = self.__proceed(obj, member, advised, access, advices, 
                                            index+1, args, kwargs)

                send_params = retval
            elif cls is commands.return_:
                if is_instance:
                    retval = command.retval

                generator.close()
                advices[index][1] = None

                return retval
            elif cls is commands.arguments:
                send_params = (args, kwargs)
            elif cls is commands.advised:
                send_params = advised
            elif cls is commands.name:
                send_params = member
            elif cls is commands.obj:
                send_params = obj

advisor = Advisor() # singleton instance 

from .aopmeta import AOPMeta
from ._aopdescriptor import _AOPDescriptor

