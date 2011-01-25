# -*- coding: utf-8 -*-
"""i18ncontent component'schema

provides entities and relations to support multilingual entities

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from yams.buildobjs import EntityType, RelationType, String, RelationDefinition
from cubicweb.schema import (PUB_SYSTEM_ENTITY_PERMS, PUB_SYSTEM_REL_PERMS,
                             PUB_SYSTEM_ATTR_PERMS, RQLConstraint)

class Language(EntityType):
    """registered language for an application.

    See http://www.loc.gov/standards/iso639-2 for available codes.
    """
    __permissions__ = PUB_SYSTEM_ENTITY_PERMS
    code = String(required=True, maxsize=2, unique=True, description=_('ISO 639.2 Code'))
    name = String(required=True, internationalizable=True, maxsize=37,
                  description=_('ISO description'))

# provide some relation types without actual relation definitions: you should define
# them in your schema on entities which are expected to have i18n content

class pivot_lang(RelationType):
    """when this attribute is true, it indicates that the entity is the master
    translation, e.g. other translation are done using it as reference.
    """
    __permissions__ = PUB_SYSTEM_ATTR_PERMS
    object = 'Boolean'
    default = False
    # see hooks for more constraints (avoid violation of translation 2nd constraint)


class lang(RelationType):
    """relation to the language used by an entity."""
    __permissions__ = PUB_SYSTEM_REL_PERMS
    # Note: can't be inlined if we want to use this relation with entities from
    #       an external source
    object = 'Language'
    cardinality = '?*'

class translation_of(RelationType):
    """indicate that an entity is a translation of another. The object of the
    relation is the master document.
    """
    __permissions__ = PUB_SYSTEM_REL_PERMS
    cardinality = '?*'
    # see hooks for more constraints
    constraints = [RQLConstraint('S lang L1, NOT O lang L1'),
                   RQLConstraint('S pivot_lang False, O pivot_lang True')]
