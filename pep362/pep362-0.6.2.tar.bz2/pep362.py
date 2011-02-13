import inspect
from operator import attrgetter


class BindError(TypeError):
    """Represent a failure of inspect.Signature.bind() being able to to
    determine if a binding of arguments to parameters is possible."""
    pass


class Parameter(object):

    """Represent a parameter in a function signature.

    Each parameter has the following attributes:

    * name
        The name of the parameter.
    * position
        The position in the parameter list for the argument, no including any
        variable position argument.
    * keyword_only
        True if the parameter is keyword-only.

    And the following optoinal attributes:

    * default_value
        The default value for the parameter, if one exists.
    * annotation
        The annoation for the parameter, if one exists.

    """

    def __init__(self, name, position, has_default=False, default_value=None,
                 keyword_only=False, has_annotation=False, annotation=None):
        """Initialize a Parameter instance.

        For has_* arguments, if they are False then the corresponding *
        parameter is ignored.

        """
        self.name = name
        self.position = position
        if has_default:
            self.default_value = default_value
        self.keyword_only = keyword_only
        if has_annotation:
            self.annotation = annotation


class Signature(object):

    """Object to represent the signature of a function/method.

    Attributes:
    * name
        Name of the function/method.
    * var_args
        Name of the variable positional parameter, else ''.
    * var_kw_wargs
        Name of the variable keywrod parameter, else ''.
    * var_annotations
        Dict keyed on the variable parameter names with the values of the
        annotation for the parameter.  If an annotation does not exist for a
        parameter, the key does not exist.

    Optional attributes:
    * return_annotation
        The annotation for the return value.



    """

    def __init__(self, func):
        """Initialize from a function or method object."""
        if hasattr(func, 'im_func'):
            func = func.im_func
        try:
            func_code = func.__code__
        except AttributeError:
            # Compatibility for versions < 2.6.
            func_code = func.func_code

        self.name = func.__name__

        try:
            # Unneeded once 2.x support is removed; can easily get info the
            #  "hard" way.
            argspec = inspect.getfullargspec(func)[:4]
        except AttributeError:
            # Needed only for tuple parameters.
            argspec = inspect.getargspec(func)
        parameters = {}

        # Parameter information.
        pos_count = func_code.co_argcount
        if hasattr(func_code, 'co_kwonlyargcount'):
            keyword_only_count = func_code.co_kwonlyargcount
        else:
            keyword_only_count = 0
        positional = argspec[0]
        keyword_only = func_code.co_varnames[pos_count:
                                                pos_count+keyword_only_count]
        try:
            fxn_defaults = func.__defaults__
        except AttributeError:
            # Deal with old names prior to 2.6.
            fxn_defaults = func.func_defaults
        if fxn_defaults:
            pos_default_count = len(fxn_defaults)
        else:
            pos_default_count = 0

        # Non-keyword-only parameters w/o defaults.
        non_default_count = pos_count - pos_default_count
        for index, name in enumerate(positional[:non_default_count]):
            name = self._convert_name(name)
            has_annotation, annotation = self._find_annotation(func, name)
            param = Parameter(name, index, has_default=False,
                    has_annotation=has_annotation, annotation=annotation)
            parameters[name] = param
        # ... w/ defaults.
        for offset, name in enumerate(positional[non_default_count:]):
            name = self._convert_name(name)
            has_annotation, annotation = self._find_annotation(func, name)
            default_value = fxn_defaults[offset]
            param = Parameter(name, offset+non_default_count,
                                has_default=True, default_value=default_value,
                                has_annotation=has_annotation,
                                annotation=annotation)
            parameters[name] = param
        # Keyword-only parameters.
        for offset, name in enumerate(keyword_only):
            has_annotation, annotation = self._find_annotation(func, name)
            has_default, default_value = False, None
            # hasattr check only needed for versions < 2.6.
            if (hasattr(func, '__kwdefaults__') and func.__kwdefaults__ and
                    name in func.__kwdefaults__):
                has_default = True
                default_value = func.__kwdefaults__[name]
            param = Parameter(name, offset+pos_count, keyword_only=True,
                                has_default=has_default,
                                default_value=default_value,
                                has_annotation=has_annotation,
                                annotation=annotation)
            parameters[name] = param
        # Variable parameters.
        index = pos_count + keyword_only_count
        self.var_annotations = dict()
        if func_code.co_flags & 0x04:
            self.var_args = func_code.co_varnames[index]
            has_annotation, annotation = self._find_annotation(func,
                                                                self.var_args)
            if has_annotation:
                self.var_annotations[self.var_args] = (
                                        func.__annotations__[self.var_args])
            index += 1
        else:
            self.var_args = ''
        if func_code.co_flags & 0x08:
            self.var_kw_args = func_code.co_varnames[index]
            has_annotation, annotation = self._find_annotation(func,
                                                                self.var_kw_args)
            if has_annotation:
                self.var_annotations[self.var_kw_args] = (
                                    func.__annotations__[self.var_kw_args])
            index += 1
        else:
            self.var_kw_args = ''

        self._parameters = parameters

        # Return annotation.
        if hasattr(func, '__annotations__'):
            if 'return' in func.__annotations__:
                self.return_annotation = func.__annotations__['return']

    def __getitem__(self, key):
        return self._parameters[key]

    def __iter__(self):
        return iter(sorted(self._parameters.values(), key=attrgetter('position')))

    def _find_annotation(self, func, name):
        """Return True if an annotation exists for the named parameter along
        with its annotation, else return False and None."""
        has_annotation, annotation = False, None
        if hasattr(func, '__annotations__'):
            if name in func.__annotations__:
                has_annotation = True
                annotation = func.__annotations__[name]
        return has_annotation, annotation

    def _convert_name(self, name):
        if not isinstance(name, list):
            return name
        else:
            return tuple(self._convert_name(x) for x in name)

    def bind(self, *args, **kwargs):
        """Return a dictionary mapping function arguments to their parameter
        variables, if possible.

        Multiple arguments for the same parameter using keyword arguments
        cannot be detected.

        """
        bindings = {}
        if self.var_args:
            bindings[self.var_args] = tuple()
        if self.var_kw_args:
            bindings[self.var_kw_args] = dict()
        positional = []
        keyword_only = {}

        for param in self:
            if not param.keyword_only:
                positional.append(param)
            else:
                keyword_only[param.name] = param

        # Positional arguments.
        if not self._parameters and args and self.var_args:
            bindings[self.var_args] = args
            args = tuple()
        for index, position_arg in enumerate(args[:]):
            try:
                param = positional.pop(0)
            except IndexError:
                # *args.
                if self.var_args:
                    bindings[self.var_args] = tuple(args)
                    break
                else:
                    raise BindError("too many positional arguments")
            self._tuple_bind(bindings, param.name, position_arg)
            args = args[1:]
        # Keyword arguments & default values.
        else:
            for positional_param in positional:
                param_name = positional_param.name
                if param_name in kwargs:
                    try:
                        bindings[param_name] = kwargs[param_name]
                        del kwargs[param_name]
                    except KeyError:
                        raise BindError("%r unbound" % param_name)
                else:
                    if hasattr(positional_param, 'default_value'):
                        self._tuple_bind(bindings, param_name,
                                            positional_param.default_value)
                    else:
                        raise BindError("%r parameter lacking default value" %
                                        param_name)

        # Keyword arguments.
        positional_dict = dict((param.name, param) for param in positional)
        for key, value in kwargs.copy().items():
            if key in bindings:
                raise BindError("too many arguments for %r parameter"
                                % key)
            if key in positional_dict:
                del positional_dict[key]
            # Keyword-only.
            elif key in keyword_only:
                del keyword_only[key]
            # **kwargs.
            elif self.var_kw_args:
                    bindings[self.var_kw_args][key] = value
                    continue
            else:
                raise BindError("too many keyword arguments")
            bindings[key] = value
            del kwargs[key]
        # Keyword-only default values.
        else:
            for name, param in keyword_only.items():
                if hasattr(param, 'default_value'):
                    bindings[name] = param.default_value
                else:
                    raise BindError("%s parameter lacking a default value" %
                                    name)

        return bindings

    def _tuple_bind(self, bindings, possible_tuple, value):
        """Where a tuple could be a parameter, handle binding the values to the
        tuple and storing into the bindings mapping."""
        if not isinstance(possible_tuple, tuple):
            bindings[possible_tuple] = value
        else:
            # Need to make sure that value is as long as the parameter, but not
            # vice-versa.
            error_msg = "not enough values to unpack for %r"
            tuple_iter = iter(possible_tuple)
            try:
                value_iter = iter(value)
            except TypeError:
                raise BindError(error_msg % possible_tuple)
            while True:
                try:
                    sub_param = tuple_iter.next()
                except StopIteration:
                    break
                try:
                    sub_value = value_iter.next()
                except StopIteration:
                    raise BindError(error_msg % possible_tuple)
                self._tuple_bind(bindings, sub_param, sub_value)


def signature(func):
    """Return a Signature object for the function or method.

    If possible, return the existing value stored in __signature__.  If that
    attribute does not exist, then try to store the Signature object at that
    attribute if possible (but is not required).

    """
    if hasattr(func, 'im_func'):
        func = func.im_func
    sig = Signature(func)
    if not hasattr(func, '__signature__'):
        try:
            func.__signature__ = sig
        except AttributeError:
            pass
    else:
        sig = func.__signature__

    return sig
