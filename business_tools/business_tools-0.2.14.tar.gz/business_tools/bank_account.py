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

"""Bank account support."""

class AccountNumber(object):
    """
    Generic base for bank account numbers.
    """
    _value = None

    def __init__(self, value):
        """
        @param value: A valid finnish bank account number.

        Should not be instantiated. Subclass instead.

        """
        self._value = value

    def bank_name(self):
        """
        Extract bank name from the account number.
        """
        return get_bank_name(self._value)

    def machine_format(self):
        """
        Return machine parseable account number.

        """
        return self._value


class BBAN(AccountNumber):
    """
    Finnish bank account number.
    """

    def __init__(self, value):
        """
        @param value: A valid finnish bank account number.

        """
        super(BBAN, self).__init__(value)
        if not BBAN.validate_account_number(value):
            raise ValueError('Invalid finnish BBAN')
        self._value = self.to_machine(value)

    def to_machine(self, value):
        """Convert value to machine parseable account number.
        @param value: A valid account number.

        """
        return self.expand_account_number(value)

    def human_format(self):
        """
        Return human readable account number.

        """
        return self.humanize_account_number(self._value)

    def __str__(self):
        """
        Return human formatted account number as string.

        """
        return self.human_format()

    @staticmethod
    def humanize_account_number(value):
        """Convert value to human formatted account number."""
        retval = value[0:6] + '-' + str(int(value[6:]))
        return retval

    @staticmethod
    def expand_account_number(number):
        """
        Transform account number to machine readable form
        """

        number = str(number).replace(' ', '')
        number = number.replace('-', '')

        # Every account number has at least 6 + 2 digits
        if len(number) < 6 + 2 or len(number) > 14:
            return False

        # Sp, Pop, Aktia, and Osuuspankki use a different method for
        # expanding the account number
        if number[0] in ['4', '5']:
            number = number[0:7] + '0' * (14 - len(number)) + number[7:]
        else:
            number = number[0:6] + '0' * (14 - len(number)) + number[6:]

        return number

    @staticmethod
    def calculate_account_number_checksum(number):
        print ("Deprecated method calculate_account_number" \
               "_checksum.")
        return BBAN.calculate_checksum(number)

    @staticmethod
    def calculate_checksum(number):
        """
        Return calculated checksum.
        """
        # Digits in the account number are multiplied by 2, 1, 2, 1, 2 ...
        # and the single digits resulting are summed together
        checksum_str = ''
        try:
            for i in range(13):
                value = int(number[i])
                checksum_str += str(value * (2 - i % 2))
        except ValueError:
            return None

        checksum = 0
        for value in checksum_str:
            checksum += int(value)

        # The checksum digit is the sum subtracted from the next whole ten
        checksum = 10 - checksum % 10
        if checksum == 10:
            checksum = 0

        return str(checksum)

    @staticmethod
    def validate_account_number(number):
        """
        Validates a Finnish bank account number.
        """
        number = BBAN.expand_account_number(number)
        if not number:
            return False

        checksum = BBAN.calculate_account_number_checksum(number)
        if checksum is None:
            return False

        return number[-1] == checksum

    @staticmethod
    def is_valid(number):
        """Validate account number."""
        return BBAN.validate_account_number(number)


class IBAN(AccountNumber):
    """
    International bank account number.
    """

    def __init__(self, value):
        super(IBAN, self).__init__(value)
        if not IBAN.validate_account_number(str(value)):
            raise ValueError('Invalid IBAN')
        self._value = str(value)

    @staticmethod
    def validate_account_number(value):
        """
        Validate IBAN account number.
        """
        for i in range(2):
            if not value[i].isalpha():
                return False
        for i in range(2, len(value)):
            if not value[i].isdigit():
                return False
        if value[2:4] != IBAN.calculate_checksum(value[4:],
                                                 value[0:2]):
            return False
        return True

    @staticmethod
    def calculate_checksum(bban, country_code='FI'):
        """
        Return calculated checksum.
        """
        if country_code != 'FI':
            raise ValueError('Only finnish account numbers are supported.')

        def letters_to_digits(data):
            new_data = ''
            for value in data:
                if value.isalpha():
                    new_data += str(ord(value) - 55)
                else:
                    new_data += value
            return new_data

        value = 98 - (int(letters_to_digits(str(bban) + 'FI00')) % 97)
        return '%.2d' % (value, )

    def bank_name(self):
        """
        Extract bank name from the account number.
        """
        return get_bank_name(iban_to_bban(self))

    def __str__(self):
        return self._value


def iban_to_bban(value):
    """
    Convert IBAN to BBAN. Return bban string in human format.
    """
    if not isinstance(value, IBAN):
        raise TypeError()
    return BBAN(value.machine_format()[4:]).human_format()


def bban_to_iban(value, country_code='FI'):
    """
    Convert BBAN to IBAN.
    """
    if not isinstance(value, BBAN):
        raise TypeError()
    account = value.machine_format()
    checksum = IBAN.calculate_checksum(account, 'FI')
    return country_code + checksum + account


def get_bank_name(account_number):
    """
    Returns the bank name based on the account number
    @param account_number: a Finnish bank account number (BBAN).
    @return: Bank name or 'Tuntematon'.
    """

    banks = {
        '1': u'Nordea',
        '2': u'Nordea',
        '31': u'Handelsbanken',
        '33': u'SEB',
        '34': u'Danske Bank',
        '36': u'Tapiola',
        '37': u'DnB NOR',
        '38': u'Swedbank',
        '39': u'S-Pankki',
        '4': u'Säästöpankki',
        '47': u'Pop',
        '5': u'Osuuspankki',
        '6': u'Ålandsbanken',
        '8': u'Sampo',
    }

    if account_number == '500001':
        return 'OKO pankki'

    # 4055xx = Helsingin Aktia
    # 4050xx = Porvoon Aktia
    # 4970xx = Vaasan Aktia
    elif account_number[0:4] in ('4055', '4050', '4970'):
        return 'Aktia'
    elif account_number[0:2] in banks:
        return banks[account_number[0:2]]
    elif account_number[0] in banks:
        return banks[account_number[0]]
    else:
        return u'Tuntematon'


def get_swift_code(bank_name):
    """
    Return a SWIFT (BIC) code for a known finnish bank.
    @param bank_name: A finnish bank name in lower case.
    @return: SWIFT-code (str) or None
    """
    data = {u'nordea': 'NDEAFIHH',
            u'nandelsbanken': 'HANDFIHH',
            u'seb': 'ESSEFIHX',
            u'danske bank': 'DABAFIHX',
            u'tapiola': 'TAPIFI22',
            u'dnb nor': 'DNBAFIHX',
            u'swedbank': 'SWEDFIHH',
            u's-pankki': 'SBANFIHH',
            u'säästöpankki': 'HELSFIHH',
            u'pop': 'HELSFIHH',
            u'osuuspankki': 'OKOYFIHH',
            u'ålandsbanken': 'AABAFI22',
            u'sampo': 'DABAFIHH',
            u'aktia': 'HELSFIHH'}
    bank_name = bank_name.lower()
    if bank_name in data:
        return data[bank_name]
    return None
