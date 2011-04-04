"""Common configuration constants
"""
from Products.CMFCore.permissions import AddPortalContent

PROJECTNAME = "collective.types.externalsearch"
IMAGE_KEY = 'image'
ADD_PERMISSIONS = {
    'collective.types.ExternalSearch': AddPortalContent,
    }
