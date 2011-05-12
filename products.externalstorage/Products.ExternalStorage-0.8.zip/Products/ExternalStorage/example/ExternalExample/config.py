from Products.CMFCore.permissions import AddPortalContent
from Products.Archetypes.public import DisplayList

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "ExternalExample"
SKINS_DIR = 'skins'

GLOBALS = globals()

ARTICLE_GROUPS = DisplayList((
    ('headline', 'Headline'),
    ('bulletin', 'Special Bulletin'),
    ('column', 'Weekly Column'),
    ('editorial', 'Editorial'),
    ('release', 'Press Release'),
    ))
