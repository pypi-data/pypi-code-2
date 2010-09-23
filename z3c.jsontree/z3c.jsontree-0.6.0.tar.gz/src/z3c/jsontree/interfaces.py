##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
from zope.contentprovider.interfaces import IContentProvider

# DOM id and name for json tree ``<UL>`` tag
JSON_TREE_ID = u'z3cJSONTree'
JSON_TREE_VIEW_NAME = u'@@SelectedManagementView.html'

JSON_TOGGLE_ICON_COLLAPSED = 'z3cJSONTreeCollapsedIcon'
JSON_TOGGLE_ICON_EXPANDED = 'z3cJSONTreeExpandedIcon'
JSON_TOGGLE_ICON_STATIC = 'z3cJSONTreeStaticIcon'

JSON_LI_CSS_EXPANDED = u'z3cJSONTreeExpanded'
JSON_LI_CSS_COLLAPSED = u'z3cJSONTreeCollapsed'
JSON_LI_CSS_STATIC = u'z3cJSONTreeStatic'

STATE_EXPANDED = 'expanded'
STATE_COLLAPSED = 'collapsed'
STATE_STATIC = 'static'


class ISubItemAware(zope.interface.Interface):
    """Sub item aware object."""


class ITreeItems(zope.interface.Interface):
    """Knows the items listed in tree for the given context."""

    def __init__(context, request, tree):
        """Adapts the context and the request.
        
        This allows to use different adapters for different layers on the same
        context.
        """

    subItems = zope.interface.Attribute(
        """List of (name, item, hasSubItems) tuple.""")


class IElementProvider(IContentProvider):

    state = zope.interface.Attribute(
        """The collapsed, expanded or static state .""")

    childTags = zope.interface.Attribute(
        """A list of rendered child tags.""")

    viewName = zope.interface.Attribute(
        """The view name which get called on the context.""")

    collapsedCSSName = zope.interface.Attribute(
        """Class name for the collapsed <LI> tag.""")
    expandedCSSName = zope.interface.Attribute(
        """Class name for the expanded <LI> tag.""")
    staticCSSName = zope.interface.Attribute(
        """Class name for the static <LI> tag.""")

    # context icon
    iconName = zope.interface.Attribute(
        """The icon name for the context icon.""")

    # toggle icon
    collapsedIconName = zope.interface.Attribute(
        """The icon name for the collapsed icon.""")
    expandedIconNamen = zope.interface.Attribute(
        """The icon name for the expanded icon.""")
    staticIconName = zope.interface.Attribute(
        """The icon name for the static icon.""")

    # properties
    className = zope.interface.Attribute(
        """The CSS class name for the rendered <LI> tag.""")

    toggleIcon = zope.interface.Attribute(
        """The toggle icon including settings for json url.""")

    icon = zope.interface.Attribute("""The icon for the given context.""")

    name = zope.interface.Attribute("""The context name""")

    url = zope.interface.Attribute("""The context url""")

    def update():
        """Must get called before render."""

    def render():
        """Render the template."""


# content provider using templates
class ILITagProvider(IElementProvider):
    """Content provider for ``LI`` tag."""


class IULTagProvider(IElementProvider):
    """Content provider for ``UL`` tag."""


class ITreeProvider(IElementProvider):
    """Content provider for tree (main) ``UL`` tag."""


# tree renderer interfaces
class ITreeRenderer(zope.interface.Interface):
    """Knows how to render elements fo the tree items."""

    def renderLI(name, item):
        """Renders <LI> tags."""

    def renderUL(name, item, childTags=None):
        """Renders <li> tag including rendered child tags."""

    tree = zope.interface.Attribute(
        """Renders <ul> tree tag including rendered child tags.""")


class IPythonRenderer(ITreeRenderer):
    """Uses python methods for rendering the tree items."""


class ITemplateRenderer(ITreeRenderer):
    """Uses IContentProvider classes within templates for rendereing the items.
    """


class IIdGenerator(zope.interface.Interface):
    """Knows how to get ids for the tree items."""

    def getId(item):
        """Returns the DOM id for a given object.

        Note: we encode the upper case letters because the Dom element id are 
        not case sensitive in HTML. We prefix each upper case letter with ':'.
        """

    def id():
        """Returns the DOM id for a given context."""


class IJSONTree(ITreeRenderer, IIdGenerator):
    """Complete JSON tree definition.
    
    Don't care about the javascript part, just implement all methods define in 
    this interfaces.
    """


class ISimpleJSONTree(IJSONTree):
    """Simple JSON tree implementation.
    
    Simple JSON tree using inline methods for rendering elements and
    traversable path for item lookup.
    """


class IGenericJSONTree(IJSONTree):
    """Generic template based JSON tree implementation.

    This implementation uses IContentProvider for element tag rendering.
    This content provider are responsible for represent a node. This allows us 
    to embed html or javascript code in the html representation in a smart 
    way. This makes it possible to include html forms in a tree node.
    """
