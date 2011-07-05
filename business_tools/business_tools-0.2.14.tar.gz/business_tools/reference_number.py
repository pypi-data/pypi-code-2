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
Reference number feature.
"""

class ReferenceNumber(object):
    """
    Datatype for bank transaction reference number.
    """

    def __init__(self, value):
        """
        >>> r = ReferenceNumber('12344')
        >>>
        """
        if not ReferenceNumber.validate(value):
            raise ValueError
        self._value = value

    def human_format(self):
        """Return reference number in human readable format"""
        return ReferenceNumber.group(self._value)

    def machine_format(self):
        """Return reference number in machine readable format"""
        ref = self._value.replace(' ', '')
        return '0' * (20 - len(ref)) + ref

    def __repr__(self):
        return '<Reference number: %s>' % self.human_format()

    def __str__(self):
        """
        Return unformatted value as string.
        """
        return str(self._value)

    def __unicode__(self):
        """
        Return unformatted value as unicode.
        """
        return unicode(self._value)

    @staticmethod
    def group(reference):
        """
        Reference number should be in groups of five digits from the right.
        Zeros in the beginning of the reference should be removed.
        """

        # Remove spaces
        reference = reference.replace(' ', '')

        # Remove leading zeros
        reference = reference.lstrip('0')

        if len(reference) < 6:
            return reference

        # Group it (first position)
        pos = len(reference) % 5
        if pos == 0:
            pos = 5

        ret = reference[:pos] # the first group
        for i in range(pos, len(reference), 5):
            ret += ' ' + reference[i:i + 5]
        return ret

    @staticmethod
    def is_valid(reference):
        """
        Validate reference number.
        """
        return ReferenceNumber.validate(reference)

    @staticmethod
    def validate(reference):
        """
        Validates a Finnish invoice reference number.

        XXX: Will be renamed to is_valid in the future.
        """

        # None is not a valid reference
        if not reference:
            return False

        # An empty string reference is valid
        if isinstance(reference, basestring) and len(reference)==0:
            return True

        reference = reference.replace(' ', '')
        if len(reference) == 0 or len(reference) > 20:
            return False

        checksum_digit = reference[-1]
        checksum = ReferenceNumber.calculate_checksum(reference[:-1])

        if checksum is None:
            return False

        return checksum_digit == checksum

    @staticmethod
    def calculate_checksum(reference):
        """
        Calculates checksum for a Finnish invoice reference number.

        Returns the checksum or raises ValueError if the checksum can't
        be calculated because the given reference contains non-digit
        characters.
        """

        # No checksum for empty reference
        if not reference:
            raise ValueError

        weight = [7, 3, 1]

        # Remove spaces and invert the string
        reference = reference.replace(' ', '')[::-1]

        checksum = 0
        for i in range(len(reference)):
            value = int(reference[i])
            checksum += weight[i % 3] * value

        # The checksum digit is the sum subtracted from the next whole ten
        checksum = 10 - checksum % 10
        if checksum == 10:
            checksum = 0

        return str(checksum)
