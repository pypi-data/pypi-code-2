"""Common configuration constants
"""

# TODO: to be removed
from Products.Archetypes.atapi import DisplayList

PROJECTNAME = 'Products.Organization'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Organization': 'Products.Organization: Add Organization',
}

# TODO: to be removed
# To be used in the InstantMessage priority field definition
MESSAGE_PRIORITIES = DisplayList((
    ('high', 'High Priority'),
    ('normal', 'Normal Priority'),
    ('low', 'Low Priority'),
    ))