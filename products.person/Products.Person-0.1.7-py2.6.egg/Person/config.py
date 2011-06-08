"""Common configuration constants
"""

# TODO: to be removed
from Products.Archetypes.atapi import DisplayList

PROJECTNAME = 'Products.Person'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Person': 'Products.Person: Add Person',
}

# TODO: to be removed
# To be used in the InstantMessage priority field definition
MESSAGE_PRIORITIES = DisplayList((
    ('high', 'High Priority'),
    ('normal', 'Normal Priority'),
    ('low', 'Low Priority'),
    ))