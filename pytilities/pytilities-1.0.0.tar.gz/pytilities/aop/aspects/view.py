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
from pytilities.aop import AOPMeta
from pytilities import aop

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
            self.__obj = obj
            aspect.apply(self.__obj)
            aspect.disable(self.__obj)

        def __advice(self):
            aspect.enable(self.__obj)
            yield aop.proceed
            aspect.disable(self.__obj)

    _delegation_aspect.apply(View)

    return View

_delegation_aspect = DelegationAspect(
    AttributeDescriptor('_View__obj'), 
    '*')

