# Copyright (c) 2007 ifPeople, Kapil Thangavelu, and Contributors
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from zope import schema
from zope.schema.interfaces import ValidationError
from Products.validation import validation
v_isemail = validation.validatorFor('isEmail')

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid')

class InvalidPhoneNumber(ValidationError):
    __doc__ = _(u"Only digit character allowed.")

class InvalidCreditCardNumber(ValidationError):
    __doc__ = _(u"Invalid Credit Card Number.")

class InvalidWeight( ValidationError ):
    __doc__ = _(u"Invalid Weight")
    
class InvalidEmail(ValidationError):
    __doc__ = _(u"Invalid Email")
    
def weightValidator( weight ):
    if weight <= 0:
        raise InvalidWeight( weight )
    return True

def emailValidator(email):
    if v_isemail(str(email)) is not 1:
        raise InvalidEmail(email)
    return True

def creditCardValid(card_number):
    """ checks to make sure that the card passes a luhn mod-10 checksum """
    # strip any whitespace
    card_number = card_number.replace(' ', '').strip()
    
    if isinstance( card_number, unicode ) and not card_number.isnumeric():
        return False
    
    elif isinstance( card_number, str) and not card_number.isdigit():
        return False

    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1
    for count in range( 0, num_digits):
        digit = int(card_number[count])
        if not (( count & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9
        sum = sum + digit
    return ( (sum % 10) == 0 )

class PhoneNumber( schema.TextLine):

    def _validate(self, value):
        super(PhoneNumber, self)._validate(value)
        if value and not value.isdigit():
            raise InvalidPhoneNumber(value)

class CreditCardNumber( schema.TextLine ):

    def _validate(self, value):
        super(CreditCardNumber, self)._validate(value)
        if not creditCardValid( value ):
            raise InvalidCreditCardNumber(value)
