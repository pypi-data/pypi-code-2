"""\
A converter which sets an error if the value doesn't match the regular expression.
"""

import re

from conversionkit import message
from conversionkit.exception import ConversionKitError
from stringconvert import StringConvertError

def matchRegex(
    regex, 
    strip=False, 
    options=None, 
    msg_no_match="Value does not match %(regex)s"
):
    ops = 0
    if options is not None:
        if not isinstance(options, list):
            raise ConversionKitError(
                "The options argument should be a list of strings"
            )
        for option in options:
            if isinstance(option, basestring):
                ops |= getattr(re, option)
            else:
                ops |= option
    cregex = re.compile(regex, ops)

    def matchRegex_converter(conversion, state=None):
        if not isinstance(conversion.value, unicode):
            raise StringConvertError(
                'The value %r is not a Unicode object'%conversion.value
            )
        if strip and isinstance(conversion.value, basestring):
            result = conversion.value.strip()
        else:
            result = conversion.value
        match = cregex.match(result)
        # Check if any of string is matched
        if not match:
            conversion.error = message(
                state, 
                msg_no_match,
                dict(regex=regex)
            )
        # Check if whole string is matched
        elif len(result) != match.end():
            conversion.error = message(
                state, 
                msg_no_match,
                dict(regex=regex)
            )
        else:
            conversion.result = result
    return matchRegex_converter


