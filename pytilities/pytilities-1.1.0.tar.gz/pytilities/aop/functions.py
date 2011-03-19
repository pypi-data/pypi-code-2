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

from .advisor import advisor

def _wrapped_call(obj, name, f, args, kwargs):
    '''
    Used for handling call to returned callables of get

    This allows for support of bound methods, ...
    '''
    original_f = f
    # f: the originally returned func
    if hasattr(f, '__self__'): # bound beastie?
        # unbind
        args = (f.__self__,) + args
        f = f.__func__ # get the original func and use that instead

    return advisor.process_call(obj, name, f, 'call', args, kwargs,
                                original_f)

