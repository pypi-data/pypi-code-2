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

"""
Delegation utilities

These utilities are a front-end to the aop package.
"""

# Note: User won't delegate any private vars, or at least shouldn't. So no
# mangling should be done in this package

__docformat__ = 'reStructuredText'

# place these in our namespace, naughty naughty
from .delegationaspect import DelegationAspect
from .profile import Profile
from .decorators import profile_carrier, in_profile

