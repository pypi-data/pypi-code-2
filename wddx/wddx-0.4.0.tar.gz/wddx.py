"""
Create Python objects from WDDX strings and files.
"""

from datetime import datetime
import io
import xml.etree.ElementTree as etree

def load(path, encoding='utf-8'):
    """
    Deserialise a WDDX file to a Python object.
    """
    with io.open(path, 'rt', encoding=encoding) as fp:
        return loads(fp.read())


def loads(xml):
    """
    Deserialise a WDDX string to a Python object
    """
    data = []
    tree = etree.fromstring(xml)
    for elem in tree.find('./data'):
        data.append(_get_value(elem))
    return data


def _tag_struct(elem):
    """
    Create dictionary from struct tag.
    """
    value = {}
    for var in elem:
        assert var.tag == 'var', "Children of struct must be var elements"
        name = var.attrib['name']
        children = list(var)
        assert len(children) == 1, "Only one child element expected"
        value[name] = _get_value(children[0])
    return value


def _tag_array(elem):
    """
    Create list from array tag.
    """
    value = []
    for e in elem:
        value.append(_get_value(e))
    return value


# Switch statement?  We don't need no stinkin' switch statement! :-)
_TAGS = {
    'array': _tag_array,
    'boolean': lambda x: True if x.attrib['value'] == 'true' else False,
    'dateTime': lambda x: datetime.strptime(x.text, "%Y-%m-%dT%H:%M:%S"),
    'null': lambda x: None,
    'number': lambda x: float(x.text) if '.' in x.text else int(x.text),
    'string': lambda x: x.text,
    'struct': _tag_struct,
}


def _get_value(elem):
    """
    Extract value of appropriate type from input element.
    """
    tag = elem.tag
    if tag not in _TAGS:
        raise ValueError("Unknown tag '{}'".format(elem.tag))
    value = _TAGS[elem.tag](elem)
    return value

