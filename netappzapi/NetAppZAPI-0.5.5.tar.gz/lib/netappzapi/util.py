#
# Utility functions
#

import logging
import debug
log = logging.getLogger('zapi')

def substituteVariables(str, namespace={}):
    """
    Perform variable substitution, given a string and a namespace.
    """
    try:
        str = str % namespace
        return str
    except KeyError, e:
        log.error("Cannot perform substitution on string. KeyError on: %s, %s", str, e)
        raise

def build_dict(node):
    """
    Create a dictionary representing an XML tree. Assumes
    the XML tree is only one layer deep.
    """
    result = {}
    for child in node:
        name = str(child.tag)
        result[name] = str(child.text)
        pass
    return result

