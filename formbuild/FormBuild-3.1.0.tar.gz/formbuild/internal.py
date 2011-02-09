"""\
Helpers only to be used internally by FormBuild to provide the ``Form`` class
"""

import logging
from cgi import escape

from bn import HTMLFragment

log = logging.getLogger(__name__)

def html_open(name, close, attributes):
    """\
    Returns an HTML open tag for ``name`` with everything properly escaped.
    """
    fragment = HTMLFragment()
    fragment.safe("<")
    fragment.write(name)
    for k, v in attributes.items():
        fragment.write(' %s="%s"'%(k, v))
    if close:
        fragment.safe(" />")
    else:
        fragment.safe(">")
    return fragment.getvalue()

def html_close(name):
    """\
    Returns an HTML close tag for ``name``
    """
    fragment = HTMLFragment()
    fragment.safe("</")
    fragment.write(name)
    fragment.safe(">")
    return fragment.getvalue()

def check_attributes(attributes, to_exclude):
    if attributes is None:
        return {}
    attribute_keys = [key.lower() for key in attributes]
    for attribute in to_exclude:
        if attribute in attribute_keys:
            raise Exception(
                "You cannot directly specify %r as a form attribute, "
                "instead use the correct API for the field you are trying "
                "to create" % (
                    attribute,
                )
            )
    return attributes.copy()
   
def handle_input(type, name, value, attributes):
    attributes = check_attributes(attributes, ['type', 'name', 'value'])
    attributes.update(
        dict(
            type=type, 
            name=name, 
        )
    )
    if value is not None:
        attributes['value'] = value
    return html_open('input', True, attributes)

def _split(name):
    parsed_options = []
    for part in name.split('.'):
        parts = part.split('[')
        name = parts[0]
        number = None
        if len(parts):
            number = parts[1].replace(']', '')
        parsed_options.append((name, number))
    return parsed_options

def group(
    name, 
    selected_values, 
    options, 
    group_type, 
    align='horiz', 
    cols=4, 
    sub_name=None
):
    if not group_type in ['checkbox', 'radio']:
        raise Exception('Invalid group type %s'%group_type)
    fragment = HTMLFragment()
    # Now parse the options string
    # Here we want people.interests.id to be the option for all keys of the form
    # people[*].interests[*].id as well as any with a number in the brackets

    #if len(options):
    #    counter = 0
    #    for pair in options:
    #        if not isinstance(pair, (tuple, list)):
    #            raise Exception(
    #                'Expected option item %s to be a list of tuples, '
    #                'not %r' % (
    #                    counter, 
    #                    pair,
    #                )
    #            )
    #        if not len(pair) == 2:
    #            raise Exception(
    #                'Expected option item %s to have be a (value, label) '
    #                'pair, not %r' % (
    #                    counter, 
    #                    pair,
    #                )
    #            )
    #    counter += 1
    ## This should not be necessary if we are being strict
    #if not isinstance(selected_values, list) and not \
    #   isinstance(selected_values, tuple):
    #    values = [unicode(selected_values)]
    #else:
    #    values = []
    #    for value in selected_values:
    #        values.append(unicode(value))
    item_counter = 0
    actual_name = name
    if len(options) > 0:
        if align <> 'table':
            for option in options:
                if len(option):
                    v=unicode(option[0])
                    k=unicode(option[1])
                else:
                    k, v = unicode(option), unicode(option)
                checked=u''
                # This isn't a good enough check
                if unicode(v) in selected_values:
                    checked=' checked="checked"'
                break_ = u'\n'
                if align == 'vert':
                    break_=u'<br />\n'
                fragment.safe('<input type="')
                # It was checked earlier, so it is safe
                fragment.safe(group_type) 
                fragment.safe('" name="')
                if sub_name:
                    fragment.write(name)
                    fragment.safe('[%s].'%(item_counter))
                    fragment.write(sub_name)
                else:
                    fragment.write(name)
                fragment.safe('" value="')
                fragment.write(unicode(v))
                fragment.safe('"'+checked+' /> ')
                fragment.write(unicode(k))
                fragment.safe(break_)
                item_counter += 1
        else:
            fragment.safe(
                u'<table border="0" width="100%" cellpadding="0" '
                u'cellspacing="0">\n    <tr>\n'
            )
            counter = -1
            for option in options:
                counter += 1
                if ((counter % cols) == 0) and (counter <> 0):
                    fragment.safe(u'    </tr>\n    <tr>\n')
                fragment.safe('      <td>')
                checked=u''
                align=u''
                if len(option):
                    v=unicode(option[0])
                    k=unicode(option[1])
                else:
                    k, v = unicode(option), unicode(option)
                if unicode(v) in selected_values:
                    checked=' checked="checked"'
                break_ = u'</td>\n      <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>\n'
                fragment.safe('<input type="')
                # It was checked earlier, so it is safe
                fragment.safe(group_type) 
                fragment.safe('" name="')
                if sub_name:
                    fragment.write(name)
                    fragment.safe('[%s].'%(item_counter))
                    fragment.write(sub_name)
                else:
                    fragment.write(name)
                fragment.safe('" value="')
                fragment.write(unicode(v))
                fragment.safe('"'+checked+' /> ')
                fragment.write(unicode(k))
                fragment.safe(break_)
                item_counter += 1
            counter += 1
            while (counter % cols):
                counter += 1
                fragment.safe(
		    u'      <td></td>\n      '
		    u'<td>&nbsp;&nbsp;&nbsp;&nbsp;</td>\n'
		)
            fragment.safe(u'    </tr>\n</table>\n')
    return fragment.getvalue()[:-1]

def _checkable(checked, type, name, value, attributes=None):
    attributes = check_attributes(
        attributes, 
        ['type', 'name', 'checked', 'value'],
    )
    attributes.update(
        dict(
            type=type, 
            name=name, 
            value=value,
        )
    )
    if checked.get(name, False) is True:
        attributes['checked'] = u'checked'
    return html_open('input', True, attributes)

def _select(
    value,
    options,
    multiple, 
    name, 
    attributes=None,
    get_option_attributes=None,
    self=None,
):
    """\
    Private method for generating ``<select>`` fields.

    You should use ``dropdown()`` for single value selects or ``combo()``
    for multi-value selects.
    """
    attributes = check_attributes(attributes, ['name', 'multiple'])
    if multiple:
        attributes['multiple'] = 'multiple'
    attributes['name'] = name
    value = unicode(value)
    fragment = HTMLFragment()
    fragment.safe(html_open(u'select', False, attributes)+'\n')
    counter = 0
    for v, k in options:
        if get_option_attributes:
            option_attr = get_option_attributes(self, v, k)
        else: 
            option_attr = {}
        option_attr = check_attributes(option_attr, ['value', 'selected'])
        if unicode(v) in value:
            option_attr['selected'] = 'selected'
        option_attr['value'] = v
        fragment.safe(html_open(u'option', False, option_attr))
        fragment.write(k)
        fragment.safe('</option>\n')
    fragment.safe(u'</select>')
    return fragment.getvalue()

