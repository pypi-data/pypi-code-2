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

from pytilities.descriptors import AttributeDescriptor
from pytilities.delegation import DelegationAspect
from pytilities.aop import AOPMeta, Aspect
from pytilities import aop
from pytilities.dictionary import FunctionMap

def create_view(aspect):

    '''
    Create a View class.

    Instances of the view delegate all access to an inner object. Before
    delegating they enable the given aspect, at the end of the access the
    aspect is disabled.

    :param aspect: The aspect to enable during viewing, and disable 
                   otherwise
    :type aspect: Aspect
    '''

    class View(object, metaclass=AOPMeta):

        '''
        A view of something
        
        The given aspect is enabled when you look through the view, disabled 
        otherwise.
        '''

        def __init__(self, obj):
            '''
            Create a view.

            :param obj: the object to look at through the view
            '''
            self.__wrapped_object = obj
            aspect.apply(self.__wrapped_object)
            aspect.disable(self.__wrapped_object)

        _aspect = aspect


    _delegation_aspect.apply(View)
    _view_aspect.apply(View)

    return View

class _ViewAspect(Aspect):
    def __init__(self):
        Aspect.__init__(self)
        self._advice_mappings = FunctionMap(self._mapper)
        self._undefined_keys = True

    def _mapper(self, key):
        access, attribute_name = key
        if access == 'call':
            return None
        else:
            return self._advice

    def _advice(self):
        with (yield aop.suppress_aspect):
            view = yield aop.advised_instance
            aspect = view.__class__._aspect
            wrapped_object = view._View__wrapped_object
            aspect.enable(wrapped_object)
            return_value = yield aop.proceed
            aspect.disable(wrapped_object)

            if callable(return_value):
                def g(*args, **kwargs):
                    aspect.enable(wrapped_object)
                    return return_value(*args, **kwargs)
                    aspect.disable(wrapped_object)

                yield aop.return_(g)

_view_aspect = _ViewAspect()

_delegation_aspect = DelegationAspect(
    AttributeDescriptor('_View__wrapped_object'), 
    '*')

