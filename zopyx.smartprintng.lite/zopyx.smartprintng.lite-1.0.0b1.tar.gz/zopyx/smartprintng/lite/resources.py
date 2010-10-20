################################################################
# zopyx.smartprintng.plone
# (C) 2009,  ZOPYX Limited & Co. KG, D-72070 Tuebingen, Germany
################################################################

""" 
Resources registry for templates, styles etc.
"""

import os

# mapping name -> directory
resources_registry = dict()

def registerResource(name, directory):
    if not os.path.exists(directory):
        raise IOError('Directory "%s" does not exit' % directory)
    resources_registry[name] = directory
