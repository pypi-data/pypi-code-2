##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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
"""Grok components"""

from zope import component, interface
from zope.viewlet.manager import ViewletManagerBase
from zope.viewlet.viewlet import ViewletBase

from grokcore.viewlet import interfaces, util


class ViewletManager(ViewletManagerBase):
    interface.implements(interfaces.IViewletManager)

    template = None

    def __init__(self, context, request, view):
        super(ViewletManager, self).__init__(context, request, view)
        self.context = context
        self.request = request
        self.view = view
        self.__name__ = self.__view_name__
        self.static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.module_info.package_dotted_name,
            )

    def sort(self, viewlets):
        """Sort the viewlets.

        ``viewlets`` is a list of tuples of the form (name, viewlet).
        """
        # In Grok, the default order of the viewlets is determined by
        # util.sort_components. util.sort_components() however expects
        # a list of just components, but sort() is supposed to deal
        # with a list of (name, viewlet) tuples.
        # To handle this situation we first store the name part on the
        # viewlet, then use util.sort_components() and then "unpack"
        # the name from the viewlet and recreate the list of (name,
        # viewlet) tuples, now in the correct order.
        s_viewlets = []
        for name, viewlet in viewlets:
            # Stuff away viewlet name so we can later retrieve it.
            # XXX We loose name information in case the same viewlet
            # is in the viewlets list twice, but with a different
            # name. Most probably this situation doesn't occur.
            viewlet.__viewlet_name__ = name
            s_viewlets.append(viewlet)
        s_viewlets = util.sort_components(s_viewlets)
        return [(viewlet.__viewlet_name__, viewlet) for viewlet in s_viewlets]

    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['static'] = self.static
        namespace['view'] = self.view
        namespace['viewletmanager'] = self
        return namespace

    def namespace(self):
        return {}

    def update(self):
        super(ViewletManager, self).update()
        # Filter out the unavailable viewlets *after* the viewlet's update()
        # has been called.
        self.viewlets = filter(lambda v: v.available(), self.viewlets)

    def render(self):
        """See zope.contentprovider.interfaces.IContentProvider"""
        # Now render the view
        if self.template:
            return self.template.render(self)
        else:
            return u'\n'.join([viewlet.render() for viewlet in self.viewlets])


class Viewlet(ViewletBase):
    """Batteries included viewlet.
    """

    def __init__(self, context, request, view, manager):
        super(Viewlet, self).__init__(context, request, view, manager)
        self.context = context
        self.request = request
        self.view = view
        self.viewletmanager = manager
        self.__name__ = self.__view_name__
        self.static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.module_info.package_dotted_name,
            )

    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['static'] = self.static
        namespace['view'] = self.view
        namespace['viewlet'] = self
        namespace['viewletmanager'] = self.manager
        return namespace

    def namespace(self):
        return {}

    def update(self):
        pass

    def available(self):
        """Return True if this viewlet is to be rendered. False otherwise.

        Note that the available() method is called *after* update() but
        *before* render() has been called.
        """
        return True

    def render(self):
        return self.template.render(self)
