#!/usr/bin/env python
# encoding: utf-8
"""
interfaces.py

Created by Manabu Terada on 2010-08-12.
Copyright (c) 2010 CMScom. All rights reserved.
"""
from zope.interface import Interface
from zope.schema import Bool, Int, List, TextLine

from c2.app.shorturl import ShortUrlMessageFactory as _


class IShortUrlSchema(Interface):
    
    base_url = TextLine(title=_(u'Base URL'), default=u"",
            description=_(u'Prefix URL (eg: http://www.cmscom.jp)'))

    folder_id = TextLine(title=_(u'Folder ID'), default=u"",
            description=_(u'Container for Short URL'))


class IShortUrlConfig(IShortUrlSchema):
    """ utility to hold the configuration related to Short URL """
