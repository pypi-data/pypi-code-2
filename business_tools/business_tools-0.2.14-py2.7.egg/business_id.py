# coding: utf-8
#
# Copyright (c) 2009, Norfello Oy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Norfello Oy nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY NORFELLO OY ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORFELLO OY BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Finnish business id support.
"""

import re

# Regexp for matching business id's
business_id_re = re.compile('^(FI|)'
                            '(([0-9]{6,8})' # match 12345671
                            '|([0-9]{6,7}-[0-9]{1})' # match 1234567-1
                            ')$', re.VERBOSE)


class BusinessID(object):
    """
    BusinessID stores finnish business id's

    A ValueError is thrown if initialized with incorrect id.


    business_id is internally stored in machine format.
    """

    # Weight for checksum calculation for company id
    weight = [2, 4, 8, 5, 10, 9, 7]

    def __init__(self, value=None):
        """
        Create a BusinessID object.

        @param value: A valid finnish business id.

        >>> from business_tools import BusinessID
        >>> BusinessID('1234567-1')
        1234567-1

        """
        self._value = None
        self._set_value(value)

    def human_format(self):
        """
        Return business id in human readable format.

        >>> b = BusinessID('1234567-1')
        >>> b.human_format()
        '1234567-1'
        """
        return self._value[:7] + '-' + self._value[7]

    def machine_format(self):
        """
        Return business id in machine parseable format.

        >>> b = BusinessID('1234567-1')
        >>> b.machine_format()
        '12345671'

        """
        return BusinessID.expand(self._value)

    def international_format(self):
        """
        Return international formatting of a finnish business id.

        >>> b = BusinessID('1234567-1')
        >>> b.international_format()
        'FI12345671'

        """
        return 'FI' + self.machine_format()

    def get_value(self):
        """
        Getter for self._value
        """
        return self._value

    def _set_value(self, value):
        """
        Setter for self._value.

        @param value: A valid finnish business id.

        """
        if not BusinessID.is_valid(value):
            raise ValueError
        self._value = BusinessID.expand(value)

    def __unicode__(self):
        """
        Return human formatted unicode() business id.
        """
        return unicode(self.human_format())

    def __str__(self):
        """
        Return human formatted str() business id.
        """
        return self.human_format()

    def __repr__(self):
        return self.human_format()

    def __ne__(self, value):
        return not self.__eq__(value)

    def __eq__(self, value):
        if not isinstance(value, BusinessID) and value == None:
            return False

        return self.get_value() == BusinessID(value).get_value()

    @staticmethod
    def split(business_id):
        """
        Split a company id to a id number part and a checksum digit.

        @param business_id: a valid finnish business id.
        """

        val = str(business_id)

        if len(val) == 0:
            return ('', '')

        parts = val.split('-')
        if len(parts) == 1:
            return (parts[0][:-1], parts[0][-1])
        else:
            return (parts[0], parts[1])

    @staticmethod
    def calculate_checksum(business_id):
        """
        Calculates checksum for a Finnish company id called Y-tunnus.

        Returns the one digit checksum in a integer or None if the given
        business id is empty or invalid.

        @param business_id: a finnish business id without checksum.
        @return: One digit checksum.
        """

        # No checksum for empty id
        if len(business_id) == 0:
            return None

        # Weighted sum of digits in the id from right to left
        business_id = business_id[::-1] # reverse
        checksum = 0
        for i in range(len(business_id)):
            try:
                value = int(business_id[i])
            except ValueError:
                return False
            checksum += value * BusinessID.weight[i]

        checksum %= 11
        if checksum == 0:
            return str(0)
        elif checksum == 1:
            return None
        else:
            return str(11 - checksum)

    @staticmethod
    def is_valid(business_id):
        """
        Validates a Finnish company id called Y-tunnus.

        The company id has seven digits and a single checksum digit at the end.
        The checksum may be separated from the main id with a hyphen '-'.

        @param business_id: a finnish business id in human or machine readable
        format
        @return: True or False.
        """
        if not business_id_re.match(unicode(business_id)):
            return False

        business_id = BusinessID.remove_country_code(business_id)
        business_id, checksum_digit = BusinessID.split(business_id)

        if not business_id or len(business_id) == 0 \
               or len(business_id) > 7 \
               or len(checksum_digit) != 1:
            return False

        checksum = BusinessID.calculate_checksum(business_id)
        if checksum is None:
            return False
        return checksum_digit == checksum

    @staticmethod
    def expand(business_id):
        """
        Expands a Finnish company id to its full length
        (7 digits + 1 checksum digit).

        A possible hyphen between id number part and the checksum digit is
        removed.

        @param business_id: a finnish business id in human or machine readable
        @return: Expanded finnish business id.
        """
        business_id = BusinessID.remove_country_code(business_id)
        business_id, checksum = BusinessID.split(business_id)
        # Left pad id with zeros
        return '0' * (7 - len(business_id)) + business_id + checksum

    @staticmethod
    def remove_country_code(business_id):
        """
        Remove leading countrycode component.
        """
        if isinstance(business_id, basestring) \
               and not business_id[0:2].isdigit():
            if business_id[0:2] != 'FI':
                raise ValueError
            return business_id[2:]
        return business_id
