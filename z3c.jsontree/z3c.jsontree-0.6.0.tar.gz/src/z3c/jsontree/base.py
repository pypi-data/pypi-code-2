##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = 'restructuredtext'

import string
import zope.interface
import zope.component
from zope.traversing import api
from zope.traversing.browser import absoluteURL
from zope.traversing.namespace import getResource
from zope.contentprovider.interfaces import IContentProvider
from zope.component import hooks

from z3c.template.template import getPageTemplate

from z3c.jsontree import interfaces
from z3c.jsontree.interfaces import JSON_TREE_ID
from z3c.jsontree.interfaces import JSON_TREE_VIEW_NAME
from z3c.jsontree.interfaces import JSON_TOGGLE_ICON_COLLAPSED
from z3c.jsontree.interfaces import JSON_TOGGLE_ICON_EXPANDED
from z3c.jsontree.interfaces import JSON_TOGGLE_ICON_STATIC
from z3c.jsontree.interfaces import JSON_LI_CSS_EXPANDED
from z3c.jsontree.interfaces import JSON_LI_CSS_COLLAPSED
from z3c.jsontree.interfaces import JSON_LI_CSS_STATIC
from z3c.jsontree.interfaces import STATE_EXPANDED
from z3c.jsontree.interfaces import STATE_COLLAPSED
from z3c.jsontree.interfaces import STATE_STATIC
from z3c.jsontree import subitem
from z3c.jsontree import util


class IdGenerator(object):
    """This mixin class generates Object Ids based on the the objects path.

    Note: The objects must be traversable by it's path. You can implement a 
    a custom path traverse concept in the getObjectByPath it you need to use
    another traverse concept.

    This ids must conform the w3c recommendation described in:
    http://www.w3.org/TR/1999/REC-html401-19991224/types.html#type-name
    """

    def getId(self, item):
        """Returns the DOM id for a given object.

        Note: we encode the upper case letters because the Dom element id are 
        not case sensitive in HTML. We prefix each upper case letter with ':'.
        """
        path = api.getPath(item)
        newPath = u''
        for letter in path:
            if letter in string.uppercase:
                newPath += ':' + letter
            else:
                newPath += letter

        # we use a dot as a root representation, this avoids to get the same id
        # for the ul and the first li tag
        if newPath == '/':
            newPath = '.'
        # add additinal dot which separates the tree id and the path, is used
        # for get the tree id out of the string in the javascript using
        # ids = id.split("."); treeId = ids[0];
        id = self.z3cJSONTreeId +'.'+ newPath
        # convert '/' path separator to marker '::', because the path '/'' is  
        # not allowed as DOM id. See also:
        # http://www.w3.org/TR/1999/REC-html401-19991224/types.html#type-name
        return id.replace('/', '::')

    def id(self):
        """Returns the DOM id for a given context."""
        return self.getId(self.context)


class TreeBase(subitem.SubItemAware):
    """Tree iterator base implementation."""

    root = None
    childTags = None
    rootChilds = None
    items = []

    z3cJSONTreeId = JSON_TREE_ID
    z3cJSONTreeName = JSON_TREE_ID
    z3cJSONTreeClass = JSON_TREE_ID

    viewName = JSON_TREE_VIEW_NAME

    # LI tag CSS names
    collapsedCSSName = JSON_LI_CSS_COLLAPSED
    expandedCSSName = JSON_LI_CSS_EXPANDED
    staticCSSName = JSON_LI_CSS_STATIC

    # toggle icon names
    collapsedIconName = JSON_TOGGLE_ICON_COLLAPSED
    expandedIconNamen = JSON_TOGGLE_ICON_EXPANDED
    staticIconName = JSON_TOGGLE_ICON_STATIC

    def getRoot(self):
        if not self.root:
            self.root = hooks.getSite()
        return self.root

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getIconURL(self, item, request, name='icon'):
        return util.getIconURL(item, request, name=name)

    def getParents(self):
        """This method returns a parent chain.
        
        The method is also responsible for skip objects which should get
        excluded e.g. the sitemanager items.
        """
        root = self.getRoot()
        return util.getParentsFromContextToObject(self.context, root)

    def update(self):
        """Update HTML code for representing a <ul> tag tree with the 
        siblings and parents of an object.

        There is only one branch expanded, in other words, the tree is
        filled with the object, its siblings and its parents with
        their respective siblings. This tree is stateless.

        If we access the tree via a virtual host, the root is adjusted to
        the right root object.

        The childTags get used in every implementation of this package. The
        items in the childTags can get rendered with the python renderer which
        uses inline code or with the template based renderer which is probably 
        slower then the python renderer becaue of it's tal usage.
        """
        childTags = None
        stackItem = self.context
        parents = self.getParents()

        for item in parents:
            tagList = []
            append = tagList.append

            for name, subItem, hasSubItems in self.getSubItems(item):
                if hasSubItems:
                    if subItem == stackItem:
                        append(self.renderUL(name, subItem, childTags))
                    else:
                        append(self.renderUL(name, subItem))
                else:
                    append(self.renderLI(name, subItem))

            childTags = ' '.join(tagList)
            stackItem = item

        self.childTags = childTags


class ProviderBase(object):
    """Base class for tag element provider."""

    template = getPageTemplate()

    root = None
    state = None
    name = None
    childTags = None
    iconName = 'icon'

    z3cJSONTreeId = JSON_TREE_ID
    z3cJSONTreeName = JSON_TREE_ID
    z3cJSONTreeClass = JSON_TREE_ID

    viewName = JSON_TREE_VIEW_NAME

    # LI tag CSS names
    collapsedCSSName = JSON_LI_CSS_COLLAPSED
    expandedCSSName = JSON_LI_CSS_EXPANDED
    staticCSSName = JSON_LI_CSS_STATIC

    # toggle icon names
    collapsedIconName = JSON_TOGGLE_ICON_COLLAPSED
    expandedIconNamen = JSON_TOGGLE_ICON_EXPANDED
    staticIconName = JSON_TOGGLE_ICON_STATIC

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    @property
    def className(self):
        if self.state == STATE_COLLAPSED:
            return self.collapsedCSSName
        elif self.state == STATE_EXPANDED:
            return self.expandedCSSName
        else:
            return self.staticCSSName

    @property
    def toggleIcon(self):
        """Returns a toggle icon including settings for json url."""
        if self.state == STATE_COLLAPSED:
            iconName = self.collapsedIconName
        elif self.state == STATE_EXPANDED:
            iconName = self.expandedIconNamen
        else:
            iconName = self.staticIconName
        icon = zope.component.getMultiAdapter((self.context, self.request), 
            name=iconName)
        resource = getResource(icon.context, icon.rname, self.request)
        src = resource()
        longDescURL = absoluteURL(self.context, self.request)
        return ('<img src="%s" alt="toggle icon" width="%s" height="%s" ' 
                'border="0" longDesc="%s" />' % (src, icon.width, 
                   icon.height, longDescURL))

    def icon(self):
        """Returns a additional named icon for the given context."""
        icon = zope.component.queryMultiAdapter((self.context, self.request), 
            name=self.iconName)
        if icon is not None:
            resource = getResource(icon.context, icon.rname, self.request)
            src = resource()
            return ('<img src="%s" alt="icon" width="%s" height="%s" ' 
                    'border="0" />' % (src, icon.width, icon.height))
        return u''

    @property
    def url(self):
        return absoluteURL(self.context, self.request) +'/'+ self.viewName

    def update(self):
        pass

    def render(self):
        return self.template()


class PythonRenderer(object):
    """Mixin class for template less tree generation.
    
    This renderer is responsible for rendering all HTML elements for the items
    found in the tree. This means evrey item will be presented in the same way.
    Use this renderer only if you like to get the same representation for each
    item. If you need custom representation for each item, use the template 
    based renderer which allows you to define for each item a custom class and
    template.
    """

    zope.interface.implements(interfaces.IPythonRenderer)

    @property
    def rootName(self):
        root = self.getRoot()
        name = api.getName(self.root)
        if not name:
            name = u'[top]'
        return name

    def getToggleIcon(self, item, state):
        """Returns a toggle icon including settings for json url."""
        if state == STATE_COLLAPSED:
            iconName = self.collapsedIconName
        elif state == STATE_EXPANDED:
            iconName = self.expandedIconNamen
        else:
            iconName = self.staticIconName
        icon = zope.component.getMultiAdapter((item, self.request), 
            name=iconName)
        resource = getResource(icon.context, icon.rname, self.request)
        src = resource()
        longDescURL = absoluteURL(item, self.request)
        return ('<img src="%s" alt="toggle icon" width="%s" height="%s" ' 
                'border="0" longDesc="%s" />' % (src, icon.width, 
                   icon.height, longDescURL))

    def renderLI(self, name, item):
        url = absoluteURL(item, self.request) +'/'+ self.viewName
        iconURL = self.getIconURL(item, self.request)
        id = self.getId(item)

        res = u''
        toggleIcon = self.getToggleIcon(item, STATE_STATIC)
        res += '<li id="%s" class="%s">%s' % (id, self.staticCSSName,
            toggleIcon)
        if iconURL != '':
            res += '<img src="%s" width="16" height="16" />' % iconURL
        res += '<a href="%s">%s</a>' % (url, name)
        res += '</li>'
        return res

    def renderUL(self, name, item, childTags=None):
        """Renders <li> tag with already rendered child tags."""
        url = absoluteURL(item, self.request) +'/'+ self.viewName
        iconURL = self.getIconURL(item, self.request)
        id = self.getId(item)

        if item is self.context:
            state = STATE_COLLAPSED
            liClass = self.collapsedCSSName
        else:
            state = STATE_EXPANDED
            liClass = self.expandedCSSName

        if childTags is None:
            state = STATE_COLLAPSED
            liClass = self.collapsedCSSName
        
        toggleIcon = self.getToggleIcon(item, state)

        res = u''
        res +=  '<li id="%s" class="%s">%s' % (id, liClass, toggleIcon)
        if iconURL != '':
            res += '<img src="%s" class="" width="16" height="16" />' % iconURL
        res += '<a href="%s">%s</a>' % (url, name)
        if childTags is not None:
            res += '  <ul>%s</ul>' % childTags
        res += '</li>'
        return res

    @property
    def tree(self):
        root = self.getRoot()
        if root is None:
            raise ValueError("Missing tree root object.")
        id = self.getId(root)
        rootName = self.rootName
        url = absoluteURL(root, self.request) +'/'+ self.viewName

        # setup root item
        if self.childTags is None:
            rootChilds = ''
            liClass = self.collapsedCSSName
            state = STATE_COLLAPSED
        else:
            rootChilds = '<ul>%s</ul>' % self.childTags
            liClass = self.expandedCSSName
            state = STATE_EXPANDED

        # setup root toggle icon
        toggleIcon = self.getToggleIcon(root, state)

        # setup root link
        rootLink = '<a href="%s">%s</a>' % (url, rootName)
        rootItem = '<li id="%s" class="%s">%s%s%s</li>' % \
            (id, liClass, toggleIcon, rootLink, rootChilds)

        # render the <ul> tag tree
        z3cJSONTree = u''
        z3cJSONTree += '<ul class="%s" id="%s" name="%s">%s</ul>' % (
            self.z3cJSONTreeClass, self.z3cJSONTreeId, self.z3cJSONTreeName, rootItem)
        return z3cJSONTree


class TemplateRenderer(object):
    """Mixin class for template based tree generation.
    
    This implementation uses IContentProvider for element tag rendering. This 
    makes it very flexible.
    
    Note: Don't forget to define custom JSONTreeItems methods which reflect the
    custom rendering. Or you will get the default rendering behavior for JSON
    loaded items.
    """

    zope.interface.implements(interfaces.ITemplateRenderer)

    liProviderName = 'li'
    ulProviderName = 'ul'
    treeProviderName = 'tree'

    def renderLI(self, name, item):
        provider = zope.component.getMultiAdapter(
            (item, self.request, self), IContentProvider, 
            self.liProviderName)
        provider.name = name
        provider.state = STATE_STATIC
        provider.update()
        return provider.render()

    def renderUL(self, name, item, childTags=None):
        """Renders <li> tag with already rendered child tags."""
        if item is self.context:
            state = STATE_COLLAPSED
        else:
            state = STATE_EXPANDED

        if childTags is None:
            state = STATE_COLLAPSED

        provider = zope.component.getMultiAdapter(
            (item, self.request, self), IContentProvider, 
            self.ulProviderName)
        provider.name = name
        provider.childTags = childTags
        provider.state = state
        provider.update()
        return provider.render()

    @property
    def tree(self):
        root = self.getRoot()
        if root is None:
            raise ValueError("Missing tree root object.")

        if self.childTags is None:
            state = STATE_COLLAPSED
        else:
            state = STATE_EXPANDED

        provider = zope.component.getMultiAdapter(
            (root, self.request, self), IContentProvider, 
            self.treeProviderName)
        provider.childTags = self.childTags
        provider.state = state
        provider.update()
        return provider.render()
