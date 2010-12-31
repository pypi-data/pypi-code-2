from Products.CMFCore.utils import ContentInit
from Products.Archetypes.atapi import process_types
from Products.Archetypes.atapi import listTypes

PROJECTNAME = 'collective.membercriterion'

# poke registration

from collective.membercriterion import memberdata

def initialize(context):
    # process our custom types

    listOfTypes = listTypes(PROJECTNAME)

    content_types, constructors, ftis = process_types(
        listOfTypes,
        PROJECTNAME)

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        ContentInit(
            kind,
            content_types      = (atype,),
            permission         = 'collective.membercriterion: Add criteria',
            extra_constructors = (constructor,),
            ).initialize(context)

