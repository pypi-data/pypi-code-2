# -*- coding: utf-8 -*-
#

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.base import registerATCT
from Products.Quota.config import *
from Products.Quota.interfaces import IQuotaAware
from Products.Quota import QuotaMessageFactory as _

quota_schema = Schema((
    StringField(
        name='sizeLimit',
        default='-1',
        schemata='metadata',
        required=False,
        languageIndependent=True,
        widget=StringWidget(
            size=40,
            label=_(u"Max size (in MB) for objects with quota"),
            description=_(u"Default maximum size of content (MB) for quota "
                           "aware containers"),
            visible={'view' : 'hidden',
                     'edit' : 'visible'},
        ),
    ),
    StringField(
        name='sizeThreshold',
        default='0',
        schemata='metadata',
        required=False,
        languageIndependent=True,
        widget=StringWidget(
            size=40,
            label=_(u"Allowed threshold (in MB) for limit for objects with "
                     "quota"),
            description=_(u"This value (MB) is added to the previous value to "
                           "make up a hard maximum size"),

            visible={'view' : 'hidden',
                     'edit' : 'visible'},
        ),
    ),
),
)

QuotaFolder_schema = ATFolder.schema.copy() + \
    quota_schema.copy()


class QuotaFolder(ATFolder):
    """
    """
    implements(IQuotaAware)
    __implements__ = (ATFolder.__implements__,)

    portal_type = 'QuotaFolder'
    archetype_name = 'QuotaFolder'
    schema =  QuotaFolder_schema

    size_limit = ATFieldProperty('sizeLimit')
    size_threshold = ATFieldProperty('sizeThreshold')

    _at_rename_after_creation = True
    _atct_newTypeFor = {'portal_type' : 'Folder',
                        'meta_type' : 'Plone Folder'}
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()


    # Enable marshalling via WebDAV/FTP/ExternalEditor.
    __dav_marshall__ = True

    security       = ClassSecurityInfo()

registerATCT(QuotaFolder, PROJECTNAME)
