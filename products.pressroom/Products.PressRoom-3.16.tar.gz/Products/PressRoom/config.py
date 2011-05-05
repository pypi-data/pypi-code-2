from Products.CMFCore.permissions import setDefaultRoles

try:
  from Products.LinguaPlone.public import *
except ImportError:
  # No multilingual support
  from Products.Archetypes.public import *

PROJECTNAME = "PressRoom"
SKINS_DIR = 'skins'
ADD_CONTENT_PERMISSION = 'PressRoom: Add portal press rooms'

setDefaultRoles(ADD_CONTENT_PERMISSION, ('Manager', 'Contributor',))

product_globals=globals()