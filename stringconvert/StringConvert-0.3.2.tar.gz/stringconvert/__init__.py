import datetime
from decimal import Decimal

from conversionkit import message
from conversionkit.exception import ConversionKitError

#
# Exceptions
#

class StringConvertError(ConversionKitError):
    pass

#
# Standard Type Converters
#

_true_values = [u'yes', u'1', u'on', u'true']
_false_values = [u'no', u'0', u'off', u'false']

def unicodeToBoolean(
    true_values=_true_values,
    false_values=_false_values,
    strip=True,
):
    def unicodeToBoolean_converter(conversion, state):
        if not isinstance(conversion.value, unicode):
            conversion.error = 'The value %r is not a Unicode object'%conversion.value
            return 
        if strip:
            input = conversion.value.strip().lower()
        else:
            input = conversion.value.lower()
        if input in true_values:
            conversion.result = True
        elif input in false_values:
            conversion.result = False
        else:
            conversion.error = 'Unrecognised option %r for a boolean' % (
                conversion.value
            )
    return unicodeToBoolean_converter

def unicodeToUnicode(min=None, max=None):
    if min is not None and max is not None and max < min:
        raise StringConvertError(
            'The value of max should not be smaller than the value of min'
        )
    def unicodeToUnicode_converter(conversion, state=None):
        if not isinstance(conversion.value, unicode):
            conversion.error = 'The value %r is not a Unicode object'%conversion.value
            return 
        length = len(conversion.value)
        if min is not None and length < min:
            conversion.error = message(
                state,
                'The string must contain %s characters or more'%(min,),
            )
        elif max is not None and length > max:
            conversion.error = message(
                state,
                'The string must contain %s characters or less'%(max,)
            )
        else:
            conversion.result = conversion.value
    return unicodeToUnicode_converter

def unicodeToDecimal(min=None, max=None, quantize=None):
    if min is not None and max is not None and max < min:
        raise StringConvertError(
            'The value of max should not be smaller than the value of min'
        )
    def unicodeToDecimal_converter(conversion, state=None):
        if not isinstance(conversion.value, unicode):
            conversion.error = 'The value %r is not a Unicode object'%conversion.value
            return 
        value = conversion.value
        try:
            result = Decimal(value, 2)
            if quantize is not None:
                result = result.quantize(quantize)
        # Catch *every* error
        except Exception, e:
            conversion.error = message(state, str(e))
        else:
            if min is not None and result < min:
                conversion.error = message(
                    state,
                    'The number must be greater than or equal to %s'%(min,),
                )
            elif max is not None and result > max:
                conversion.error = message(
                    state,
                    'The number must be less than or equal to %s'%(max,)
                )
            else:
                conversion.result = result
    return unicodeToDecimal_converter

def unicodeToFloat(min=None, max=None):
    if min is not None and max is not None and max < min:
        raise StringConvertError(
            'The value of max should not be smaller than the value of min'
        )
    def unicodeToFloat_converter(conversion, state=None):
        if not isinstance(conversion.value, unicode):
            conversion.error = 'The value %r is not a Unicode object'%conversion.value
            return 
        value = conversion.value
        try:
            result = float(value)
        # Catch *every* error
        except Exception, e:
            conversion.error = message(state, str(e))
        else:
            if min is not None and result < min:
                conversion.error = message(
                    state,
                    'The number must be greater than or equal to %s'%(min,),
                )
            elif max is not None and result > max:
                conversion.error = message(
                    state,
                    'The number must be less than or equal to %s'%(max,)
                )
            else:
                conversion.result = result
    return unicodeToFloat_converter

def unicodeToInteger(min=None, max=None, msg_invalid=None):
    if min is not None and max is not None and max < min:
        raise StringConvertError(
            'The value of max should not be smaller than the value of min'
        )
    def unicodeToInteger_converter(conversion, state=None):
        if not isinstance(conversion.value, unicode):
            conversion.error = 'The value %r is not a Unicode object'%conversion.value
            return 
        value = conversion.value
        try:
            result = int(value)
        # Catch *every* error
        except Exception, e:
            if msg_invalid is None:
                conversion.error = message(state, str(e))
            else:
                conversion.error = msg_invalid
        else:
            if min is not None and result < min:
                conversion.error = message(
                    state,
                    'The number must be greater than or equal to %s'%(min,)
                )
            elif max is not None and result > max:
                conversion.error = message(
                    state,
                    'The number must be less than or equal to %s'%(max,)
                )
            else:
                conversion.result = result
    return unicodeToInteger_converter

def unicodeToDatetime(format='%Y-%m-%d %H:%M', strip=True):
    def unicodeToDatetime_converter(conversion, state=None):
        if not isinstance(conversion.value, unicode):
            conversion.error = 'The value %r is not a Unicode object'%conversion.value
            return 
        if strip:
            input = conversion.value.strip()
        else:
            input = conversion.value
        try:
            conversion.result = datetime.datetime.strptime(
                input, 
                format
            )
        except ValueError, e:
            conversion.error = message(state, str(e))
    return unicodeToDatetime_converter

def unicodeToTime(format='%H:%M', strip=True):
    def unicodeToTime_converter(conversion, state=None):
        if not isinstance(conversion.value, unicode):
            conversion.error = 'The value %r is not a Unicode object'%conversion.value
            return 
        if strip:
            input = conversion.value.strip()
        else:
            input = conversion.value
        try:
            result = datetime.datetime.strptime(
                input,
                format
            )
        except ValueError, e:
            conversion.error = message(state, str(e))
        else:
            conversion.result = datetime.time(
                result.hour, 
                result.minute, 
                result.second
            )
    return unicodeToTime_converter

def unicodeToDate(format='%Y-%m-%d', strip=True):
    # Catch a common problem:
    if '%M' in format:
        raise StringConvertError(
            'The date format cannot accept a minutes argument (%M)'
        )
    def unicodeToDate_converter(conversion, state=None):
        if not isinstance(conversion.value, unicode):
            conversion.error = 'The value %r is not a Unicode object'%conversion.value
            return 
        if strip:
            input = conversion.value.strip()
        else:
            input = conversion.value
        try:
            result = datetime.datetime.strptime(
                input, 
                format
            )
        except ValueError, e:
            conversion.error = message(state, str(e))
        else:
            conversion.result = datetime.date(
                result.year, 
                result.month, 
                result.day
            )
    return unicodeToDate_converter

def stringToUnicode(encoding='utf8', errors='strict'):
    """\
    Decodes the string using the codec registered for encoding. ``encoding``
    defaults to ``utf8``. ``errors`` may be given to set a different error handling
    scheme. The default is ``'strict'``, meaning that encoding errors lead to the
    conversion failing. Other possible values are ``'ignore'``, ``'replace'`` and
    any other name registered via the ``codecs`` module ``register_error()``
    function.
    """
    def stringToUnicode_converter(conversion, state=None):
        try:
            conversion.result = conversion.value.decode(encoding, errors)
        except Exception, e:
            conversion.error = str(e)
    return stringToUnicode_converter

def toUnicode(raise_on_error=False):
    def toUnicode_converter(conversion, state=None):
        try:
            conversion.result = unicode(conversion.value)
        except Exception, e:
            if raise_on_error:
                raise
            conversion.error = str(e)
    return toUnicode_converter

