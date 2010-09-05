### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from hurry.query.interfaces import IQuery
from interfaces.category import ICategory, ICategoryManager, ICategoryManagerTarget
from interfaces.category import ICategorizedContent, ICategoriesTarget

# import Zope3 packages
from zope.app import zapi
from zope.app.folder.folder import Folder
from zope.app.intid.interfaces import IIntIds
from zope.component import adapts
from zope.interface import implements, alsoProvides
from zope.location import locate
from zope.proxy import setProxiedObject, ProxyBase
from zope.schema.fieldproperty import FieldProperty

# import local packages
from hurry.query.set import AnyOf
from ztfy.i18n.property import I18nTextProperty
from ztfy.workflow.interfaces import IWorkflowContent

from ztfy.blog import _


class Category(Folder):
    """Category persistence class"""

    implements(ICategory)

    title = I18nTextProperty(ICategory['title'])
    shortname = I18nTextProperty(ICategory['shortname'])
    heading = I18nTextProperty(ICategory['heading'])

    def getVisibleTopics(self):
        """See `ICategory` interface"""
        intids = zapi.getUtility(IIntIds)
        query = zapi.getUtility(IQuery)
        results = query.searchResults(AnyOf(('Catalog', 'categories'), (intids.queryId(self),)))
        return sorted([v for v in results if IWorkflowContent(v).isVisible()],
                      key=lambda x: IWorkflowContent(x).publication_effective_date,
                      reverse=True)


CATEGORY_MANAGER_ANNOTATIONS_KEY = 'ztfy.blog.category.manager'

class CategoryManagerAdapter(ProxyBase):

    adapts(ICategoryManagerTarget)
    implements(ICategoryManager)

    def __init__(self, context):
        annotations = IAnnotations(context)
        manager = annotations.get(CATEGORY_MANAGER_ANNOTATIONS_KEY)
        if manager is None:
            manager = annotations[CATEGORY_MANAGER_ANNOTATIONS_KEY] = Category()
            alsoProvides(manager, ICategoryManager)
            locate(manager, context, '++category++')
        setProxiedObject(self, manager)


class CategoriesList(Persistent):
    """Content categories container"""

    implements(ICategorizedContent)

    categories = FieldProperty(ICategorizedContent['categories'])

    @property
    def categories_ids(self):
        intids = zapi.getUtility(IIntIds)
        return [intids.register(cat) for cat in self.categories]


CATEGORIES_ANNOTATIONS_KEY = 'ztfy.blog.category.content'

class CategorizedContentAdapter(ProxyBase):
    """Content categories adapter"""

    adapts(ICategoriesTarget)
    implements(ICategorizedContent)

    def __init__(self, context):
        annotations = IAnnotations(context)
        container = annotations.get(CATEGORIES_ANNOTATIONS_KEY)
        if container is None:
            container = annotations[CATEGORIES_ANNOTATIONS_KEY] = CategoriesList()
        setProxiedObject(self, container)
