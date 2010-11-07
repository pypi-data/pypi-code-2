"""Common configuration constants
"""

PROJECTNAME = 'metascapes.web2cache'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
}

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here
##/code-section config-bottom


# Load custom configuration not managed by archgenxml
try:
    from metascapes.web2cache.AppConfig import *
except ImportError:
    pass
