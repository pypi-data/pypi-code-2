### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages
from persistent import Persistent

# import Zope3 interfaces
from z3c.language.switch.interfaces import II18n
from zope.annotation.interfaces import IAnnotations
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from interfaces.resource import IResource, IResourceContainer, IResourceContainerTarget

# import Zope3 packages
from zope.app import zapi
from zope.app.container.contained import Contained
from zope.component import adapts
from zope.interface import implements, classProvides
from zope.location import locate
from zope.proxy import setProxiedObject, ProxyBase
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.security.proxy import removeSecurityProxy

# import local packages
from ordered import OrderedContainer
from ztfy.extfile.blob import BlobFile, BlobImage
from ztfy.file.property import FileProperty
from ztfy.i18n.property import I18nTextProperty
from ztfy.utils.traversing import getParent

from ztfy.blog import _


class Resource(Persistent, Contained):

    implements(IResource)

    title = I18nTextProperty(IResource['title'])
    description = I18nTextProperty(IResource['description'])
    content = FileProperty(IResource['content'], klass=BlobFile, img_klass=BlobImage)
    filename = FieldProperty(IResource['filename'])
    language = FieldProperty(IResource['language'])


class ResourceContainer(OrderedContainer):

    implements(IResourceContainer)


RESOURCES_ANNOTATIONS_KEY = 'ztfy.blog.resource.container'

class ResourceContainerAdapter(ProxyBase):
    """Resources container adapter"""

    adapts(IResourceContainerTarget)
    implements(IResourceContainer)

    def __init__(self, context):
        annotations = IAnnotations(context)
        container = annotations.get(RESOURCES_ANNOTATIONS_KEY)
        if container is None:
            container = annotations[RESOURCES_ANNOTATIONS_KEY] = ResourceContainer()
            locate(container, context, '++static++')
        setProxiedObject(self, container)


class ResourceContainerResourcesVocabulary(SimpleVocabulary):
    """List of resources of a given content"""

    classProvides(IVocabularyFactory)

    def __init__(self, context):
        container = getParent(context, IResourceContainerTarget)
        terms = [SimpleTerm(removeSecurityProxy(r), zapi.getName(r), II18n(r).queryAttribute('title') or '{{ %s }}' % r.filename) for r in IResourceContainer(container).values()]
        super(ResourceContainerResourcesVocabulary, self).__init__(terms)
