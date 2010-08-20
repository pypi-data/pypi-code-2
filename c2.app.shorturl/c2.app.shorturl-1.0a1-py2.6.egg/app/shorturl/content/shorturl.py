# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from zope import interface
from zope.component import queryUtility

from Products.Archetypes.atapi import *
from Products.CMFCore.utils import getToolByName
# from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.configuration import zconf

from c2.app.shorturl import ShortUrlMessageFactory as _
from c2.app.shorturl.content.interfaces import IShortUrl
from c2.app.shorturl.config import *
from c2.app.shorturl.interfaces import IShortUrlConfig

try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False

try:
    from plone.i18n.normalizer.ja import _gethashed
    JA_NORMALIZE = True
except ImportError:
    JA_NORMALIZE = False

MAX_LEN = 5 #TODO:

schema = Schema((
    StringField('suffix_url',
            required=False,
            searchable=False,
            widget = StringWidget(
                    description = "",
                    description_msgid = "help_suffix_url",
                    label = "suffix_url",
                    label_msgid = "label_suffix_url",
                    i18n_domain = "c2.app.shortulr")),

    StringField('org_path',
            required=False,
            searchable=False,
            widget = StringWidget(
                    description = "",
                    description_msgid = "help_org_pathl",
                    label = "org_path",
                    label_msgid = "label_org_path",
                    i18n_domain = "c2.app.shortulr")),
),)
shorturl_schema = getattr(ATCTContent, 'schema', Schema(())).copy() + schema.copy()
finalizeATCTSchema(shorturl_schema)

class ShortUrl(ATCTContent):
    """
    """
    security = ClassSecurityInfo()
    interface.implements(IShortUrl)
    schema = shorturl_schema

    meta_type = "ShortUrl"
    _at_rename_after_creation = True

    def get_org_url(self):
        url = self.getSuffix_url()
        if url.startswith('http'):
            return url
        config = queryUtility(IShortUrlConfig)
        base_url = getattr(config, 'base_url', '') #TODO: Check
        if not base_url.endswith('/'):
            base_url += '/'
        if url.startswith('/'):
            url = url[1:]
        return base_url + url
    
    def generateNewId(self):
        """Suggest an id for this object.
        This id is used when automatically renaming an object after creation.
        /Products/Archetypes/BaseObject.py(735)generateNewId()
        """
        if not JA_NORMALIZE:
            return None
        new_id = "".join(_gethashed(self.get_org_url(), MAX_LEN))
        
        if not new_id:
            return None

        # Don't do anything without the plone.i18n package
        if not URL_NORMALIZER:
            return None

        if not isinstance(new_id, unicode):
            charset = self.getCharset()
            new_id = unicode(new_id, charset)

        request = getattr(self, 'REQUEST', None)
        if request is not None:
            return IUserPreferredURLNormalizer(request).normalize(new_id)

        return queryUtility(IURLNormalizer).normalize(new_id)

registerType(ShortUrl, PROJECTNAME)
	


