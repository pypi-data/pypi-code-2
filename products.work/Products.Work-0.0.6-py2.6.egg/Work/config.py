"""Common configuration constants
"""

# TODO: to be removed
from Products.Archetypes.atapi import DisplayList

PROJECTNAME = 'Products.Work'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Work': 'Products.Work: Add Work',
}

# TODO: to be removed
# To be used in the InstantMessage priority field definition
MESSAGE_PRIORITIES = DisplayList((
    ('high', 'High Priority'),
    ('normal', 'Normal Priority'),
    ('low', 'Low Priority'),
    ))