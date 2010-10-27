from Products.Archetypes.public import DisplayList

PROJECTNAME = "SimpleBlog"

# deprecated, just here for compatability
DISPLAY_MODE = DisplayList((
    ('full', 'Full'), ('descriptionOnly', 'Description only'), ('titleOnly', 'Title only') ))

# set to 0 if you don't want entries to be folderish
# use at your own risk. this is not fully tested
ENTRY_IS_FOLDERISH = 0
