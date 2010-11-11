"""collective.redirect"""

from Products.CMFCore import utils
from Products.CMFCore import permissions
from Products.Archetypes import atapi

def initialize(context):

    import content

    listOfTypes = atapi.listTypes('collective.redirect')
    content_types, constructors, ftis = atapi.process_types(
        listOfTypes, 'collective.redirect')

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % ('collective.redirect', atype.archetype_name)
        utils.ContentInit(
            kind,
            content_types=(atype,),
            permission=permissions.AddPortalContent,
            extra_constructors=(constructor,),
            ).initialize(context)
    
