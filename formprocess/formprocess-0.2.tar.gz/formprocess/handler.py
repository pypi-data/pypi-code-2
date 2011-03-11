""" Generic web form handler class and associates. """
import logging
from decorator import decorator
from inspect import getargspec

from formencode import Invalid
from formencode.rewritingparser import html_quote
from formencode.variabledecode import variable_decode, variable_encode
from webhelpers.containers import DumbObject


log = logging.getLogger(__name__)


class FormHandler(object):
    """ Base form handler. """
    
    use_variable_encode = False
    """ True if outgoing defaults and errors are encoded.

    Formencode's variabledecode module is used for this.
    """
    
    use_variable_decode = False
    """ True if incoming defaults are decoded.

    Formencode's variabledecode module is used for this.    
    """

    prompt_defaults = None
    """ Hook method: (state) => defaults.

    Called to get the defaults for the initial display of the form.
    """
    
    on_process_error = None
    """ Hook method: (defaults, errors) => (defaults, errors, state).

    Called when an error occurs while processing the form submission.
    """
    
    end_process = None
    """ Hook method: (defaults, state) => str

    The developer can return anything they want here since its just returned
    to their code anyways.
    """
    
    update_state = None
    """ Hook method: (\*args, \*\*kwargs)

    The state is passed as a keyword argument.  This method returns nothing.
    """

    customize_fill_kwargs = None
    """ Hook method: (defaults, errors, state, fill_kwargs) => fill_kwargs

    This method is called during build_render_vars so that the developer can
    customize the fill_kwargs.
    """

    schema = None
    """ Object compatible with formencode's Schema.

    This object must provided a to_python method and raise Invalid exceptions
    exactly as formencode's Schema for compatibility with this library.

    This will used before get_schema is considered.
    """

    get_schema = None
    """ Hook method: (raw_params, state) => schema

    This method allows the developer to choose a schema at request time based
    on the submission.

    Note that the schema attribute takes precedence over this method.
    """
    
    fetch_form_params = None
    """ Hook method: (state) => raw_params

    This method is called at every request for processing to get the form
    params.
    """
    
    def make_state(self):
        """ Makes a state object and returns it. """
        return DumbObject()
    
    def _start_prompt(self, *args, **kwargs):
        assert self.schema or self.get_schema
        assert self.fetch_form_params
        state = kwargs.get('state', None)
        if state is None:
            state = self.make_state()
        if self.update_state:
            kwargs['state'] = state
            self.update_state(*args, **kwargs)
        return state
    
    def _end_prompt(self, defaults, state):
        return self.build_render_vars(defaults=defaults, state=state)
    
    def prompt(self, *args, **kwargs):
        """ Send the form to the user for the first time. """
        state = self._start_prompt(*args, **kwargs)
        if self.prompt_defaults:
            defaults = self.prompt_defaults(state)
            if self.use_variable_encode:
                defaults = variable_encode(defaults)
        else:
            defaults = None
        return self._end_prompt(defaults, state)

    def _start_process(self, *args, **kwargs):
        assert self.schema or self.get_schema
        assert self.fetch_form_params
        state = kwargs.get('state', None)
        if state is None:
            state = self.make_state()
        if self.update_state:
            kwargs['state'] = state
            self.update_state(*args, **kwargs)

        raw_params = self.fetch_form_params(state)
        if self.use_variable_decode:
            raw_params = variable_decode(raw_params)
        if not self.schema:
            schema = self.get_schema(raw_params, state)
        else:
            schema = self.schema

        try:
            defaults = schema.to_python(raw_params, state=state)
        except Invalid, e:
            return self._process_invalid(e, state=state)
        return dict(defaults=defaults, errors=None, state=state)

    def was_success(self, extra_vars):
        """ Use this when end_process returns the render_vars. """
        return not bool(extra_vars['errors'])

    def process(self, *args, **kwargs):
        """ Processes a form submission. """
        extra_vars = self._start_process(*args, **kwargs)
        if not self.was_success(extra_vars):
            return extra_vars
        else:
            defaults, state = extra_vars['defaults'], extra_vars['state']
            
        try:
            return self.end_process(defaults, state)
        except Invalid, e:
            return self._process_invalid(e, state=state)

    def decorate_prompt(self, render=None):
        """ Decorate a function that serves the role of the prompt_defaults
        hook. """
        def wrapper(f, *args, **kwargs):
            #TODO: Optimize this.
            # We have to do this otherwise kwargs gets put into args and
            # we cannot override them.
            argspec = getargspec(f)
            if not argspec[2]:
                kwargs_count = len(argspec[3])
                args_count = len(argspec[0]) - kwargs_count
                for i in range(kwargs_count):
                    kwargs[argspec[0][args_count+i]] = args[args_count+i]
                args = args[:-kwargs_count]
            state = self._start_prompt(*(args[1:]), **kwargs)
            kwargs.update(dict(state=state))
            if render is None:
                kwargs.update(dict(extra_vars=None))
            defaults = f(*args, **kwargs)
            extra_vars = self._end_prompt(defaults, state)
            if type(render) == str:
                controller_instance = args[0]
                render_method = getattr(controller_instance, render)
                return render_method(extra_vars)
            elif render is None:
                kwargs.update(dict(state=state, extra_vars=extra_vars))
                return f(*args, **kwargs)
            else:
                return render(extra_vars)
        return decorator(wrapper)

    def decorate_process(self, render=None):
        """ Decorate a function that serves the role of the end_process
        hook. """
        def wrapper(f, *args, **kwargs):
            #TODO: Optimize this.
            # We have to do this otherwise kwargs gets put into args and
            # we cannot override them.
            argspec = getargspec(f)
            if not argspec[2]:
                kwargs_count = len(argspec[3])
                args_count = len(argspec[0]) - kwargs_count
                for i in range(kwargs_count):
                    kwargs[argspec[0][args_count+i]] = args[args_count+i]
                args = args[:-kwargs_count]
            extra_vars = self._start_process(*(args[1:]), **kwargs)
                
            if not self.was_success(extra_vars):
                if type(render) == str:
                    controller_instance = args[0]
                    render_method = getattr(controller_instance, render)
                    return render_method(extra_vars)
                elif render is None:
                    kwargs.update(dict(extra_vars=extra_vars))
                    return f(*args, **kwargs)
                else:
                    return render(extra_vars)
            else:
                kwargs.update(dict(defaults=extra_vars['defaults'],
                        state=extra_vars['state']))
                # The decorated function should be expecting an extra_vars.
                if render is None:
                    kwargs.update(dict(extra_vars=None))
                try:
                    return f(*args, **kwargs)
                except Invalid, e:
                    extra_vars = self.process_invalid(e, state=extra_vars['state'])
                    if type(render) == str:
                        controller_instance = args[0]
                        render_method = getattr(controller_instance,
                                render)
                        return render_method(extra_vars)
                    elif render is None:
                        kwargs.update(dict(extra_vars=extra_vars))
                        return f(*args, **kwargs)
                    else:
                        return render(extra_vars)
        return decorator(wrapper)

    def _process_invalid(self, e, state=None):
        """ Process an Invalid exception. """
        errors = e.unpack_errors(encode_variables=self.use_variable_encode)
        if self.use_variable_encode:
            defaults = variable_encode(e.value)
        else:
            defaults = e.value
        if self.on_process_error:
            (defaults, errors) = self.on_process_error(defaults, errors,
                    state)
        return self.build_render_vars(defaults=defaults, errors=errors,
                state=state)

    def build_render_vars(self, defaults=None, errors=None, state=None):
        """ Build fill_kwargs with customizations and return render vars. """
        fill_kwargs = {}
        fill_kwargs['defaults'] = defaults
        fill_kwargs['errors'] = errors
        if self.customize_fill_kwargs:
            fill_kwargs = self.customize_fill_kwargs(defaults, errors, state,
                    fill_kwargs)
        return self.end_build_render_vars(defaults, errors, state, fill_kwargs)

    def end_build_render_vars(self, defaults, errors, state, fill_kwargs):
        """ Assemble the variables to be returned by prompt and process. """
        extra_vars = {
            'defaults': defaults,
            'errors': errors,
            'state': state,
            'fill_kwargs': fill_kwargs,
        }
        return extra_vars

    def end_process(self, defaults, state):
        """ Leave this as is if you want to handler success/error inside
        caller of process(). """
        return self.build_form_dict(defaults=defaults, errors={},
                state=state)
