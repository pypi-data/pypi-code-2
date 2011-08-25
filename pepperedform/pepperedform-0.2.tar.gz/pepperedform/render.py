"""
Tools used when rendering the form.

<%def name="form(render_kwargs)">
  <form method="POST" action="/submit">
    <%formlib:sequence render_kwargs="${render_kwargs}" name="${'dates'}" args="render_kwargs">
      <%formlib:mapping render_kwargs="${render_kwargs}" args="render_kwargs">
      ${h.text_tag(render_kwargs, 'month')}
      ${h.select_tag(render_kwargs, 'day', options=[(d, d) for d in range(31)])}
      ${h.text_tag(render_kwargs, 'year')}
      </%formlib:mapping>      
    </%formlib:sequence>
    <%formlib:rename render_kwargs="${render_kwargs}" name="${'gender'}" args="render_kwargs">
    ${h.radio_tag(render_kwargs, 'gender_male', value='male')}
    ${h.radio_tag(render_kwargs, 'gender_female', value='female')}
    </%formlib:rename>
    ${h.checkbox_tag(render_kwargs, 'Adult', value='Yes')}
    ${h.textarea_tag(render_kwargs, 'Details')}
    <input type="submit">
  </form>
</%def>
${form(render_kwargs)}

"""
from mako.runtime import supports_caller
from webhelpers.misc import NotGiven
from webhelpers.html.tags import text, textarea, checkbox, radio, select


SEQUENCE = u'sequence'
MAPPING = u'mapping'
RENAME = u'rename'


def build_id(render_kwargs, name):
    """ Build a DOM id for an html tag. """
    return u'_'.join(render_kwargs['id_stack'] + [name])


def sequence_getter(items, name, if_missing=None):
    """ A sequence should pass this function to its children to get their
    defaults or errors.
    """
    if items:
        return items
    return if_missing


def rename_getter(items, name, if_missing=None):
    """ A rename wrapper should pass this function to its children to get their
    defaults or errors.
    """
    if items:
        return items
    return if_missing

    
def mapping_getter(items, name, if_missing=None):
    """  A mapping should pass this function to its children to get their
    defaults or errors.
    """
    if items:
        return items.get(name, if_missing)
    return if_missing


def make_start_token(name, type_):
    """ Makes the special token used by peppercorn to group things. """
    value = u'{0}:{1}'.format(name, type_)
    return value


def field_error(render_kwargs, name):
    """ Gets the error for this field out of the render_kwargs. """
    return render_kwargs['getter'](render_kwargs['errors'], name, None)


def input_tag(render_kwargs, name, value=None, id=NotGiven, type='text',
        **attrs):
    getter = render_kwargs['getter']
    value = getter(render_kwargs['defaults'], name, value)
    if id is NotGiven:
        id_ = build_id(render_kwargs, name)
    attrs['_closed'] = render_kwargs.get('closed', False)
    return text(name, value=value, id=id, type=type, **attrs)


def checkbox_tag(render_kwargs, name, value='1', checked=False, label=None,
        id=NotGiven, **attrs):
    getter = render_kwargs['getter']
    checked = getter(render_kwargs['defaults'], name, False)
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    attrs['_closed'] = render_kwargs.get('closed', False)
    return checkbox(name, value=value, checked=checked, label=label, id=id,
        **attrs)


def radio_tag(render_kwargs, name, value, checked=False, label=None,
        id=NotGiven, **attrs):
    getter = render_kwargs['getter']
    checked = getter(render_kwargs['defaults'], name, False)
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    attrs['_closed'] = render_kwargs.get('closed', False)
    return radio(name, value, checked=checked, label=label, id=id, **attrs)


def textarea_tag(render_kwargs, name, content=NotGiven, id=NotGiven, **attrs):
    getter = render_kwargs['getter']
    if content is NotGiven:
        content = getter(render_kwargs['defaults'], name, u'')
    if id is NotGiven:
        id_ = build_id(render_kwargs, name)
    return textarea(name, content=content, id=id, **attrs)


def select_tag(render_kwargs, options, name, selected_values=NotGiven, 
        id=NotGiven, **attrs):
    if selected_values is NotGiven:
        selected_values = ()
    getter = render_kwargs['getter']
    selected_values = getter(render_kwargs['defaults'], name, selected_values)
    if type(selected_values) not in (tuple, list):
        selected_values = tuple([selected_values])
    if id is NotGiven:
        id = build_id(render_kwargs, name)
    return select(name, selected_values, options, id=id, **attrs)


@supports_caller
def rename(context, render_kwargs, name=None):
    value = make_start_token(name, RENAME)
    getter = render_kwargs['getter']
    defaults = getter(render_kwargs['defaults'], name)
    errors = getter(render_kwargs['errors'], name)
    new_render_kwargs = render_kwargs.copy()
    new_render_kwargs['defaults'] = defaults
    new_render_kwargs['errors'] = errors
    new_render_kwargs['getter'] = rename_getter
    if name:
        new_render_kwargs['id_stack'] = render_kwargs['id_stack'] + [name]
    else:
        new_render_kwargs['id_stack'] = render_kwargs['id_stack'][:]
    closed = render_kwargs.get('closed', False)
    context.write(text(type='hidden', name='__start__', value=value, _closed=closed))
    context['caller'].body(new_render_kwargs)
    context.write(text(type='hidden', name='__end__', value=value, _closed=closed))
    return ''


@supports_caller
def mapping(context, render_kwargs, name=None):
    value = make_start_token(name, MAPPING)
    getter = render_kwargs['getter']
    defaults = getter(render_kwargs['defaults'], name)
    errors = getter(render_kwargs['errors'], name)
    new_render_kwargs = render_kwargs.copy()
    new_render_kwargs['defaults'] = defaults
    new_render_kwargs['errors'] = errors
    new_render_kwargs['getter'] = mapping_getter
    if name:
        new_render_kwargs['id_stack'] = render_kwargs['id_stack'] + [name]
    closed = render_kwargs.get('closed', False)
    context.write(text(type='hidden', name='__start__', value=value, _closed=closed))
    context['caller'].body(new_render_kwargs)
    context.write(text(type='hidden', name='__end__', value=value, _closed=closed))
    return ''


@supports_caller
def sequence(context, render_kwargs, name=None):
    value = make_start_token(name, SEQUENCE)
    getter = render_kwargs['getter']
    defaults = getter(render_kwargs['defaults'], name)
    errors = getter(render_kwargs['errors'], name)
    if name is not None:
        id_stack = render_kwargs['id_stack'] + [name]
    else:
        id_stack = render_kwargs['id_stack'][:]
    closed = render_kwargs.get('closed', False)
    context.write(text(type='hidden', name='__start__', value=value, _closed=closed))
    if defaults:
        for index, new_defaults in enumerate(defaults):
            # Errors must be either falsy or contain an entry
            # for every entry in the defaults list, if no error then the
            # entry should be None.
            if errors:
                new_errors = errors[index]
            else:
                new_errors = None
            new_render_kwargs = render_kwargs.copy()
            new_render_kwargs['defaults'] = new_defaults
            new_render_kwargs['errors'] = new_errors
            new_render_kwargs['getter'] = sequence_getter
            new_render_kwargs['id_stack'] = id_stack + [unicode(index)]
            context['caller'].body(new_render_kwargs)
    context.write(text(type='hidden', name='__end__', value=value, _closed=closed))
    return ''

