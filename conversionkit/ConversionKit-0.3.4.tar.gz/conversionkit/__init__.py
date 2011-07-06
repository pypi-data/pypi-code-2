"""\
Conversion Toolkit

See the docs/source/manual.rst for an explanation of this module.
"""

import copy
import logging

from conversionkit.exception import ConversionKitError, ConversionError
from conversionkit.exception import APIError

log = logging.getLogger(__name__)

#
# Conversion Class
#

class Conversion(object):
    """\
    When writing converters for this conversion object you should ensure that
    converters designed to work with single values set the .result attribute
    directly whereas converters which operate on nested data structures set
    the .children attribute and leave this object to calculate the result 
    from the child conversions.
    """
    def __init__(self, value):
        self._value = value
        self._result = []
        self._error = []
        self.children = None

    def perform(self, converter, state=None, formencode_method=None):
        if self._error != [] or self._result != []:
            raise ConversionKitError(
                u'A converter has already been applied to this conversion '
                u'object'
            )
        if formencode_method is not None:
            # Use formencode compatibility mode 
            import formencode
            from formbuild import ValidationState, errors_to_dict
            try:
                validation_state = ValidationState(state)
                result = getattr(converter, formencode_method)(
                    self.value, 
                    validation_state
                )
            except formencode.Invalid, e:
                self.error = errors_to_dict(e)
            else:
                self.result = result
        else:
            if converter is None:
                raise ConversionKitError(
                    u"'None' is not a valid converter. If you are using a "
                    u"converter factory to produce a converter have you "
                    u"remembered to return the inner function?"
                )
            # Use the converter
            if isinstance(converter, (str, unicode, list, tuple, dict)):
                raise ConversionKitError(
                    u"This (%s) is not a valid converter"%type(converter)
                )
            converter(self, state)
            # Check that an error or a result has been set
            if self._result == self._error == []:
                # No error or result has been set
                raise ConversionKitError(
                    u"The converter %r doesn't work correctly, it failed to "
                    u"set a result or an error."%converter
                )
            elif self._result != [] and self._error != []:
                # No error or result has been set
                raise ConversionKitError('Faulty converter')
        return self

    def _get_error(self):
        if self._result == [] and self._error != []:
            return self._error[0]
        elif self._result == self._error == []:
            raise ConversionKitError(
                u'No conversion has been performed so no error is '
                u'present.'
            )
        elif self._result != [] and self._error == []:
            raise ConversionKitError(
                u'This conversion was successful so no error is present'
            )
        else:
            raise ConversionKitError(
                u'This conversion is an incosistent internal state. Perhaps a '
                u'faulty converters has been used.'
            )
            
    def _set_error(self, error):
        if self._result != []:
            raise ConversionKitError(
                u'You cannot set an error while a result is present'
            )
        elif self._error != []:
            raise ConversionKitError(
               u'An error has already been set on this conversion'
            )
        self._error = [error]

    def _get_result(self, internal_call=False):
        if self._error == [] and self._result != []:
            return self._result[0]
        elif self._error != [] and self._result == []:
            raise ConversionError(self._error[0], self)
        elif self._error == [] and self._result == []:
            raise ConversionKitError(
                u'No errors or result has been set. It is possible you have '
                u'forgotten to perform a conversion by calling .perform() or '
                u'that the converter you used has failed to behave correctly.'
            )
        else:
            raise ConversionKitError(
                u'This conversion is an incosistent internal state. Perhaps a '
                u'faulty converters has been used.'
            )

    def _set_result(self, result):
        if self._error != []:
            raise ConversionKitError(
                u'You cannot set a result while an error is present'
            )
        elif self._result != []:
            raise ConversionKitError(
                u'A result has already been set on this conversion'
            )
        self._result = [result]

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        raise ConversionKitError(
            u'You cannot set the value direclty. Please create a new '
            u'conversion object'
        )

    def _get_successful(self):
        """\
        Can return ``True`` or ``False``. Raises a ConversionKitError exception
        if no conversion has been performed yet.
        """
        if self._error != [] and self._result == []:
            return False
        elif self._error == [] and self._result != []:
            return True
        elif self._error == self._result == []:
            raise ConversionKitError(u'No conversion has been performed yet')
        else:
            raise ConversionKitError(
                u'This conversion is an inconsistent internal state. Perhaps a '
                u'faulty converters has been used.'
            )

    def _set_successful(self, value):
        raise ConversionKitError(
            u'You cannot set whether a conversion has been successful or not '
            u'by changing the successful attribute. Instead you should set '
            u'the error attribute or the result attribute'
        )

    # Properties (available since Python 2.2)
    result = property(_get_result, _set_result)
    error = property(_get_error, _set_error)
    value = property(_get_value, _set_value)
    successful = property(_get_successful, _set_successful)

#
# Message Translation
#

# Dummy translation function for marking strings for extraction. 
_ = lambda s: s

# All error message generation is done via the message() function below which
# itself can make use of a state.conversionkit.message() function provided by
# the user to implement localization.
def message(state, message, args=None):
    if args is None:
        args = {}
    handle = None
    if state is not None:
        if isinstance(state, dict) and state.has_key('conversionkit') and \
           isinstance(state['conversionkit'], dict) and \
           state['conversionkit'].has_key('message'):
            handle = state['conversionkit']['message']
        elif hasattr(state, 'conversionkit') and \
           isinstance(state.conversionkit, dict) and \
           state.conversionkit.has_key('message'):
            handle = state.conversionkit['message']
        elif hasattr(state, 'conversionkit') and \
           hasattr(state.conversionkit, 'message'):
            handle = state.conversionkit.message
    if not handle:
        if not args:
            return message
        return message % args
    else:
        return handle(state, message, args)

#
# Special Converters
#

def oneOf(values):
    def oneOf_converter(conversion, state=None):
        if not conversion.value in values:
            conversion.error = message (
                state,
                u'The value submitted is not one of the allowed values'
            )
        else:
            conversion.result = conversion.value
    return oneOf_converter

def tryEach(
    alternatives, 
    stop_on_first_result=True, 
    stop_on_first_error=False, 
    children_keys=None, 
    MSG_NONE_SUCCESSFUL=None
):
    def tryEach_converter(conversion, state):
        if children_keys is not None:
            conversion.children = {}
        else:
            conversion.children = []
        matched = False
        first_error = None
        for i, alternative in enumerate(alternatives):
            # This should really use the Chain code to copy properly
            input = conversion.value
            child_conversion = Conversion(input)
            child_conversion.perform(alternative, state)
            if children_keys is not None:
                conversion.children[children_keys[i]] = child_conversion
            else:
                conversion.children.append(child_conversion)
            if child_conversion.successful:
                matched = True
                if stop_on_first_result:
                    conversion.result = child_conversion.result
                    #conversion.children = child_conversion.children
                    return
            elif not first_error:
                first_error = child_conversion.error
                if stop_on_first_error:
                    conversion.error = first_error
                    #conversion.children = child_conversion.children
                    return
        if not matched:
            if MSG_NONE_SUCCESSFUL is None:
                conversion.error = first_error
            else:
                conversion.error = MSG_NONE_SUCCESSFUL
        # If we got here we didn't have any errors and 
        # stop_on_first_result was False
        if not first_error:
            if children_keys is not None:
                conversion.result = dict([(k, child.result) for k, child in conversion.children.items()])
            else:
                conversion.result = [child.result for child in conversion.children]
    return tryEach_converter

def chainConverters(*converters):
    def chainConverters_converter(conversion, state=None):
        if isinstance(conversion.value, (list, tuple)):
            # No need to create a copy for a list
            result = conversion.value
        else:
            result = copy.copy(conversion.value)
        children = conversion.children
        for converter in converters:
            if isinstance(converter, (tuple, list, str, unicode, dict)):
                raise ConversionKitError(u'%r is not a valid post-converter'%(converter,))
            child_conversion = Conversion(result)
            child_conversion.children = children
            converter(child_conversion, state)
            if not child_conversion.successful:
                set_error(conversion, child_conversion.error)
                conversion.children = child_conversion.children
                return
            else:
                result = child_conversion.result
                children = child_conversion.children
        set_result(conversion, result)
        conversion.children = children
    return chainConverters_converter

def chainPostConverters(*converters):
    def chainPostConverters_converter(conversion, state=None):
        for converter in converters:
            if isinstance(converter, (tuple, list)):
                raise ConversionKitError(u'A list %r is not a valid post-converter'%converter)
            converter(conversion, state)
            if conversion._error == [] and conversion._result == [] or \
               not hasattr(conversion, 'children'):
                raise ConversionKitError(
                    u'Converter %r did not return a used conversion object'%(
                        converter
                    )
                )
    return chainPostConverters_converter

#
# Null Converter
#

def noConversion(copy_mode='shallow'):
    if copy_mode not in ['shallow', 'deep']:
        raise ConversionKitError(u'Unknown copy mode %r'%copy_mode)
    def noConversion_converter(conversion, state=None):
        if copy_mode == 'shallow':
            conversion.result = copy.copy(conversion.value)
        elif copy_mode == 'deep':
            conversion.result = copy.deepcopy(conversion.value)
    return noConversion_converter

#
# Post-converter helper converters
#

def set_error(conversion, error):
    conversion._result = []
    conversion._error = [error]

def set_result(conversion, result):
    conversion._result = [result]
    conversion._error = []

#
# Field
#

class NoDefault(object):
    pass

no_default = NoDefault()

class Field(object):
    def __init__(
        self, 
        converter, 
        missing_error=no_default, 
        empty_error=no_default, 
        missing_default=no_default, 
        empty_default=no_default, 
        missing_or_empty_default=no_default, 
        missing_or_empty_error=no_default,
    ):
        self.empty_default = empty_default
        self.missing_default = missing_default
        self.converter = converter
        self.missing_error = missing_error
        self.empty_error = empty_error
        if missing_or_empty_default is not no_default:
            if self.missing_default is not no_default:
                raise Exception(u"You cannot specify both 'missing_default' and 'missing_or_empty_default'")
            if self.empty_default is not no_default:
                raise Exception(u"You cannot specify both 'empty_default' and 'missing_or_empty_default'")
            self.missing_default = missing_or_empty_default
            self.empty_default = missing_or_empty_default
        if missing_or_empty_error is not no_default:
            if self.missing_error is not no_default:
                raise Exception(u"You cannot specify both 'missing_error' and 'missing_or_empty_error'")
            if self.empty_error is not no_default:
                raise Exception(u"You cannot specify both 'empty_error' and 'missing_or_empty_error'")
            self.missing_error = missing_or_empty_error
            self.empty_error = missing_or_empty_error

    def __call__(self, *k, **p):
        return self.converter(*k, **p)

#
# toDict
#

class Missing(object):
    """\
    This class is used in a ``toDict()`` conversion when a field is
    missing. In order to make the handling of errors due to missing fields
    consistent with the behaviour of other errors, including empty value errors, a
    child conversion is set up for the missing field but because no value was
    present it isn't possible to set a ``.value`` attribute on the conversion so
    this class is used instead.
    """

MSG_DICTIONARY = dict(
    msg_many_invalid_fields=_(u'Multiple fields were invalid'),
    msg_some_invalid_fields=_(u'The %(fields)s fields were invalid'),
    msg_single_invalid_field=_(u'The \'%(field)s\' field is invalid'),
    msg_field_not_allowed=_(u'The field %r is not allowed'),
    msg_fields_not_allowed=_(u"The fields '%s' and '%s' are not allowed"),
)

def toDict(
    converters,

    missing_defaults = None,
    empty_defaults = None,
    missing_errors = None,
    empty_errors = None,

    missing_or_empty_errors = None,
    missing_or_empty_defaults = None,

    filter_extra_fields=True,
    allow_extra_fields=True,
    raise_on_extra_fields=True,
    use_many_message_after_failures=3,
    msg_many_invalid_fields=MSG_DICTIONARY['msg_many_invalid_fields'],
    msg_some_invalid_fields=MSG_DICTIONARY['msg_some_invalid_fields'],
    msg_single_invalid_field=MSG_DICTIONARY['msg_single_invalid_field'],
    msg_field_not_allowed=MSG_DICTIONARY['msg_field_not_allowed'],
    msg_fields_not_allowed=MSG_DICTIONARY['msg_fields_not_allowed'],
):
    """\
    This is a converter which handles pre-converters and post converters
    as well as a dictionary of converters. Rather than using this class it
    is recommended you use ``make_dictionary()`` together with the 
    ``chain()`` converter to chain any pre-handlers, dictionary converter
    and post-handlers.
    """
    if use_many_message_after_failures <= 2:
        raise ConversionKitError(
            u"The 'use_many_message_after_failures' option must contain a "
            u"value greater than or equal to 2"
        )

    if isinstance(missing_errors, (str, unicode)):
        message_ = missing_errors
        missing_errors = {}
        for k in converters.keys():
            missing_errors[k] = message_ % {'key': k}
    elif isinstance(missing_errors, (list, tuple)):
        try:
            message_, fields = missing_errors
        except ValueError:
            raise ConversionKitError(
                u"Expected the 'missing_errors' argument to be a (message, "
                u'[fieldnames...]) pair.'
            )
        missing_errors = {}
        for k in fields:
            missing_errors[k] = message_ % {'key': k}
    if isinstance(empty_errors, (str, unicode)):
        message_ = empty_errors
        empty_errors = {}
        for k in converters.keys():
            empty_errors[k] = message_ % {'key': k}
    elif isinstance(empty_errors, (list, tuple)):
        try:
            message_, fields = empty_errors
        except ValueError:
            raise ConversionKitError(
                u"Expected the 'empty_errors' argument to be a (message, "
                u'[fieldnames...]) pair.'
            )
        empty_errors = {}
        for k in fields:
            empty_errors[k] = message_ % {'key': k}

    if isinstance(missing_or_empty_errors, (str, unicode)):
        message_ = missing_or_empty_errors
        missing_or_empty_errors = {}
        for k in converters.keys():
            missing_or_empty_errors[k] = message_ % {'key': k}
    elif isinstance(missing_or_empty_errors, (list, tuple)): 
        try:
            message_, fields = missing_or_empty_errors
        except ValueError:
            raise ConversionKitError(
                u"Expected the 'empty_errors' argument to be a (message, "
                u'[fieldnames...]) pair.'
            )
        missing_or_empty_errors = {}
        for k in fields:
            missing_or_empty_errors[k] = message_ % {'key': k}

    _missing_defaults = {}
    _empty_defaults = {}
    _missing_errors = {}
    _empty_errors = {}

    if missing_or_empty_defaults:
        _missing_defaults.update(missing_or_empty_defaults)
        _empty_defaults.update(missing_or_empty_defaults)
    if missing_defaults:
        _missing_defaults.update(missing_defaults)
    if empty_defaults:
        _empty_defaults.update(empty_defaults)
    if missing_or_empty_errors:
        _missing_errors.update(missing_or_empty_errors)
        _empty_errors.update(missing_or_empty_errors)
    if missing_errors:
        _missing_errors.update(missing_errors)
    if empty_errors:
        _empty_errors.update(empty_errors)

    for k in _empty_defaults:
        if k in _empty_errors:
            raise ConversionKitError(
                u'You cannot set both an error and a default if key %r is '
                u'empty'%(k)
            )
    for k in _missing_defaults:
        if k in _missing_errors:
            raise ConversionKitError(
                u'You cannot set both an error and a default if key %r is '
                u'missing'%(k)
            )

    for name, converter in converters.items():
        if isinstance(converter, Field):
            if converter.missing_error is not no_default:
                if name in _missing_errors:
                    raise ConversionKitError(
                        u'You cannot set a missing error for key %r in both '
                        u'the Field and the toDict arguments' % name
                    )
                else:
                    _missing_errors[name] = converter.missing_error
            if converter.empty_error is not no_default:
                if name in _empty_errors:
                    raise ConversionKitError(
                        u'You cannot set an empty error for key %r in both '
                        u'the Field and the toDict arguments' % name
                    )
                else:
                    _empty_errors[name] = converter.empty_error
            if converter.missing_default is not no_default:
                if name in _missing_defaults:
                    raise ConversionKitError(
                        u'You cannot set a missing default for key %r in '
                        u'both the Field and the toDict arguments' % name
                    )
                else:
                    _missing_defaults[name] = converter.missing_default
            if converter.empty_default is not no_default:
                if name in _empty_defaults:
                    raise ConversionKitError(
                        u'You cannot set an empty default for key %r in both '
                        u'the Field and the toDict arguments' % name
                    )
                else:
                    _empty_defaults[name] = converter.empty_default
    def toDict_converter(conversion, state=None):

        if not isinstance(conversion.value, dict):
            raise Exception(
                u'Expeceted the input to be a dictionary, not %r'%(
                    conversion.value
                )
            )

        values = {}
        results = {}
        children = {}
        errors = []

        extra_fields = {}
        for k, v in conversion.value.items():
            k = unicode(k)
            if not converters.has_key(k):
                extra_fields[k] = v
            else:
                values[k] = v
        if extra_fields and allow_extra_fields is False:
            if len(extra_fields) == 1:
                error = msg_field_not_allowed%extra_fields.keys()[0]
            else:
                fields = extra_fields.keys()
                error = msg_fields_not_allowed%(
                    "', '".join(fields[0:-1]),
                    fields[-1]
                )
            if raise_on_extra_fields:
                raise ConversionKitError(error)
            else:
                conversion.error = error
                return

        # Set any errors or defaults from missing or empty fields
        to_ignore = []
        for field, error in _missing_errors.items():
            if not values.has_key(field):
                child_conversion = Conversion(Missing()).perform(noConversion())
                set_error(child_conversion, error)
                errors.append(field)
                to_ignore.append(field)
                children[field] = child_conversion
        # Set any defaults needed for missing fields
        for field, default in _missing_defaults.items():
            if not values.has_key(field):
                child_conversion = Conversion(Missing()).perform(noConversion())
                set_result(child_conversion, default)
                children[field] = child_conversion
                results[field] = default
                to_ignore.append(field)
        for k, v in values.items():
            k = unicode(k)
            if v in [None, '']:
                if k in _empty_errors:
                    child_conversion = Conversion(v).perform(noConversion())
                    set_error(child_conversion, _empty_errors[k])
                    errors.append(k)
                    to_ignore.append(k)
                    children[k] = child_conversion
                if k in _empty_defaults:
                    child_conversion = Conversion(v).perform(noConversion())
                    set_result(child_conversion, _empty_defaults[k])
                    results[k] = _empty_defaults[k]
                    children[k] = child_conversion
                    to_ignore.append(k)

        # Loop over the converters, setting up a child conversion 
        # for each one fields without a corresponding converter
        # are removed
        for key, converter in converters.items():
            if key not in to_ignore and values.has_key(key):
                child_conversion = Conversion(values[key]).perform(
                    converter, 
                    state
                )
                if not child_conversion.successful:
                    errors.append(key)
                else:
                    results[key] = child_conversion.result
                children[key] = child_conversion

        # Add the extra_fields back if they aren't supposed to be 
        # filtered
        if filter_extra_fields is False:
            for k, v in extra_fields.items():
                if results.has_key(k):
                    raise ConversionKitError(
                        u'One of the filtered fields is present '
                        u'in the results. This should not be possible'
                        u'and is likely to be a bug in the new '
                        u'implementation of toDict()'
                    )
                else:
                    children[k] = Conversion(v).perform(noConversion())
                    results[k] = copy.copy(v)
        conversion.children = children
        # We haven't set the overall error yet because we want
        # the message to be appropriate to the number of errors
        if errors:
            if len(errors) > use_many_message_after_failures:
                error = message(
                    state, 
                    msg_many_invalid_fields,
                )
            elif len(errors) > 1:
                error = message(
                    state, 
                    msg_some_invalid_fields,
                    dict(
                        fields="'"+"', '".join(errors[:-1])+\
                            "' and '"+errors[-1]+"'"
                    )
                )
            elif len(errors) == 1:
                error = message(
                    state, 
                    msg_single_invalid_field,
                    dict(field=errors[0])
                )
            conversion.error = error
        else:
            conversion.result = dict([(unicode(k), v) for k, v in results.items()])
        conversion.children = dict([(unicode(k), v) for k, v in conversion.children.items()])
    return toDict_converter

#
# ListOf Compound Converter
#

def toList(converter, min=None, max=None):
    if min is not None and max is not None and max<min:
        raise ConversionKitError(
            u'You have specified a value for max which is less than min'
        )
    if min is not None and min < 0:
        raise ConversionKitError(
            u'The value for min must be greater than or equal to 0'
        )
    if max is not None and max < 0:
        raise ConversionKitError(
            u'The value for max must be greater than or equal to 0'
        )
    def toList_converter(conversion, state=None):
        children = []
        errors = []
        result = []
        for k in conversion.value:
            child_conversion = Conversion(k)
            child_conversion.perform(converter, state)
            if not child_conversion.successful:
                errors.append(child_conversion.error)
            else:
                result.append(child_conversion.result)
            children.append(child_conversion)
        conversion.children = children
        if len(errors) >= 2:
            conversion.error = u'Some of the items were not valid'
        elif len(errors) == 1:
            conversion.error = u'One of the items was not valid'
        else:
            if min is not None and len(result) < min:
                if min == 1:
                    conversion.error = u'No items were specified'
                else:
                    conversion.error = u'There were less than %s items'%(min,)
            elif max is not None and len(result) > max:
                if max == 0:
                    conversion.error = u'No values are allowed'
                elif max == 1:
                    conversion.error = u'Only one value is allowed'
                else:
                    conversion.error = (
                        u'There are too many items in the list. The maximum '
                        u'number is %s.'%(max,)
                    )
            else:
                # This never gets set if there are errors so it will only exist
                # if *all* the children are appended and so it does't matter
                # that earlier in the function we don't append results if there
                # are errors.
                conversion.result = result
    return toList_converter

# Deprecated:
toDictionary = toDict
toListOf = toList

