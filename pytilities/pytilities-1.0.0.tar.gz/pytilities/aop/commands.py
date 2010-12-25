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

# The yielding idea was taken from http://www.cs.tut.fi/~ask/aspects/intr.shtml
# But modified quite a bit to better support multiple advice to the same
# members.

__docformat__ = 'reStructuredText'

'''
Commands that an aspect can yield back to its caller.
'''

# Note: yes these are classes, but the user of the aop needn't know that, so we
# don't use camel case here. The yields look more natural that way.
class proceed(object):
    '''
    Call advised attribute with given args when yielded.

    Don't forget to include a self argument, if needed.

    Its return is sent back to the advice.
    '''
    # Note: not using **kwargs allows passing self by kwargs
    def __init__(self, *args, kwargs = {}): 
        self.args = args
        self.kwargs = kwargs

class return_(object):
    '''
    Return last return value

    If `yield return_` is used, the return of the last `yield proceed` is used.
    If given an argument, that is used as return value.
    '''
    def __init__(self, retval):
        self.retval = retval

class arguments(object):
    '''
    Yielding arguments, will return (args, kwargs).

    Args is a tuple and kwargs a frozendict.

    Note: even though get, set, delete advice would never have kwargs; it is 
    always provided. This allows you to share the same bit of advice among
    multiple types of advice, and also be able to use the self param (the first
    arg to args, for any type of advice)
    '''
    # Put very specific, here are the args an advice may expect:
    #     - get advice: self
    #     - set advice: self, value
    #     - delete advice: self
    #     - call advice: self, other args
    # i.e. the same args the user sees when defining them on their getter,
    # setter, ... functions.
    

class advised(object):
    '''
    Yielding advised, will return the function that is advised by the aspect.

    Do not use this to call the actual function, you should use `proceed` for
    that.
    '''

class name(object):
    '''
    Yielding name, will return the name of the attribute that was called.
    '''

# You may wonder why this is useful since the first arg of calls is self;
# that isn't the case for static methods, that's where this thing comes in
# handy
class obj(object):
    '''
    Yielding obj, will return the object to which the advice was applied
    '''

