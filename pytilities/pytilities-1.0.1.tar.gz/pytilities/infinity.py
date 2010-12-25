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


'''
Provides a cross-platform alternative to the platform dependent float('inf').
'''

__docformat__ = 'reStructuredText'

# NOTE: currently it works together well with float('inf'). This support may be
# unnecessary as we're supposed to replace float('inf'). Don't advertise this
# support anywhere, we'll remove it as soon as it becomes bothersome, unless
# someone could come up with a good use case.

# Python notes:
# a == b is the same as a.__eq__(b),
# if a == b returns NotImplemented, it will try b == a
# If a < b returns NotImplemented, it will try b > a
# If a <= b returns NotImplemented, it will try b >= a

# legend of comments: ! means opposite sign

_finf = float('inf')
_fninf = float('-inf')

# Note: our inf, ... needn't even be ints, neither are finf, fninf and fnan
class _Base(object):
    def __pos__(self):
        # +num
        return self

    def __mul__(self, other):
        # inf * 0 -> nan
        # inf * nan -> nan
        # inf * neg_num -> -inf
        # inf * pos_num -> inf
        if other == 0 or is_nan(other):
            return nan
        elif other < 0:
            return -self
        else:
            return self

    def __rmul__(self, other):
        return self * other # a*b = b*a

    __imul__ = __mul__

    def __div__(self, other):
        # inf / inf -> nan
        # inf / nan -> nan
        # inf / 0 -> exception
        # inf / neg_num -> !inf
        # inf / pos_num -> inf
        if is_infinity(other) or is_nan(other):
            return nan
        elif other == 0:
            raise ZeroDivisionError
        elif other < 0:
            return -self
        else:
            return self

    def __rdiv__(self, other):
        # inf / inf -> nan
        # nan / inf -> nan
        # neg_num / inf -> -inf
        # pos_num / inf -> inf
        if is_infinity(other) or is_nan(other):
            return nan
        elif other < 0:
            return -self
        else:
            return self

    __truediv__ = __floordiv__ = __div__
    __rtruediv__ = __rfloordiv__ = __rdiv__

    def __ne__(self, other):
        return not self == other

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        return not is_nan(other) and not self >= other

    def __le__(self, other):
        return not is_nan(other) and not self > other

    def __copy__(self):
        return self

    def __radd__(self, other):
        return self + other

    __iadd__ = __radd__

    def __sub__(self, other):
        return self + (-other)

    __rsub__ = __isub__ = __sub__

class _PositiveInfinity(_Base):
    def __str__(self):
        return "+inf"

    def __eq__(self, other):
        # inf == inf -> True
        # inf == * -> False
        return is_positive_infinity(other)

    def __add__(self, other):
        # inf + !inf -> nan
        # inf + nan -> nan
        # inf + inf -> inf
        # inf + num -> inf
        if is_negative_infinity(other) or is_nan(other):
            return nan
        else:
            return self

    def __neg__(self):
        # -num
        return negative_infinity

    def __gt__(self, other):
        # inf > inf -> False
        # inf > nan -> False
        # +inf > * -> True
        if is_positive_infinity(other) or is_nan(other):
            return False
        else:
            return True

infinity = _PositiveInfinity()

class _NegativeInfinity(_Base):
    def __str__(self):
        return "-inf"

    def __eq__(self, other):
        # inf == inf -> True
        # inf == * -> False
        return is_negative_infinity(other)

    def __add__(self, other):
        # inf + !inf -> nan
        # inf + nan -> nan
        # inf + inf -> inf
        # inf + num -> inf
        if is_positive_infinity(other) or is_nan(other):
            return nan
        else:
            return self

    def __neg__(self):
        # -num
        return infinity

    def __gt__(self, other):
        # inf > inf -> False
        # inf > nan -> False
        # -inf > * -> False
        return False

negative_infinity = _NegativeInfinity()

class _NAN(_Base):
    def __mul__(self, other):
        return self

    __add__ = __rdiv__ = __div__ = __mul__

    def __eq__(self, other):
        return False

    __ge__ = __lt__ = __le__ = __gt__ = __eq__

    def __ne__(self, other):
        return True

    def __neg__(self):
        return self

    def __str__(self):
        return "nan"
    
nan = _NAN()

def is_infinity(number):
    ''':return: True if `number` is infinity or -infinity'''
    return is_positive_infinity(number) or \
            is_negative_infinity(number)

def is_positive_infinity(number):
    ''':return: True if `number` is infinity'''
    return number is infinity or number == _finf

def is_negative_infinity(number):
    ''':return: True if `number` is -infinity'''
    return number is negative_infinity or number == _fninf

def is_nan(number):
    ''':return: True if `number` is nan'''
    return str(number) == 'nan'


