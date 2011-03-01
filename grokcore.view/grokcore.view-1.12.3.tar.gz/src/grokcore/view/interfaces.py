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
"""Grok interfaces
"""
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IBrowserPage, IBrowserView


class IBaseClasses(Interface):
    View = Attribute("Base class for browser views.")
    DirectoryResource = Attribute("Base class to create new "
                                  "directory resource.")

class IDirectives(Interface):

    def layer(layer):
        """Declare the layer for the view.

        This directive acts as a contraint on the 'request' of
        grok.View. This directive can only be used on class level."""

    def path(path):
        """Declare which path to use on a DirectoryResource.

        This directive can only be used on class level."""

    def skin(skin):
        """Declare this layer as a named skin.

        This directive can only be used on class level."""

    def template(template):
        """Declare the template name for a view.

        This directive can only be used on class level."""

    def templatedir(directory):
        """Declare a directory to be searched for templates.

        By default, grok will take the name of the module as the name
        of the directory.  This can be overridden using
        ``templatedir``."""


class IGrokcoreViewAPI(IBaseClasses, IDirectives):

    def url(request, obj, name=None, data=None):
        """Generate the URL to an object with optional name attached.
        An optional argument 'data' can be a dictionary that is converted
        into a query string appended to the URL."""

    def PageTemplate(template):
        """Create a Grok PageTemplate object from ``template`` source
        text.  This can be used for inline PageTemplates."""

    def PageTemplateFile(filename):
        """Create a Grok PageTemplate object from a file specified by
        ``filename``.  It will be treated like an inline template
        created with ``PageTemplate``."""

    IBrowserRequest = Attribute('Browser request interface')
    IDefaultBrowserLayer = Attribute('Default layer for browser views.')


class IGrokView(IBrowserPage, IBrowserView):
    """Grok views all provide this interface."""

    context = Attribute('context', "Object that the view presents.")

    request = Attribute('request', "Request that the view was looked up with.")

    response = Attribute('response', "Response object that is "
                         "associated with the current request.")

    static = Attribute('static', "Directory resource containing "
                       "the static files of the view's package.")

    def redirect(url):
       """Redirect to given URL"""

    def url(obj=None, name=None, data=None):
        """Construct URL.

        If no arguments given, construct URL to view itself.

        If only obj argument is given, construct URL to obj.

        If only name is given as the first argument, construct URL
        to context/name.

        If both object and name arguments are supplied, construct
        URL to obj/name.

        Optionally pass a 'data' keyword argument which gets added to the URL
        as a cgi query string.
        """

    def default_namespace():
        """Returns a dictionary of namespaces that the template
        implementation expects to always be available.

        This method is *not* intended to be overridden by application
        developers.
        """

    def namespace():
        """Returns a dictionary that is injected in the template
        namespace in addition to the default namespace.

        This method *is* intended to be overridden by the application
        developer.
        """

    def update(**kw):
        """This method is meant to be implemented by grok.View
        subclasses.  It will be called *before* the view's associated
        template is rendered and can be used to pre-compute values
        for the template.

        update() can take arbitrary keyword parameters which will be
        filled in from the request (in that case they *must* be
        present in the request)."""

    def render(**kw):
        """A view can either be rendered by an associated template, or
        it can implement this method to render itself from Python.
        This is useful if the view's output isn't XML/HTML but
        something computed in Python (plain text, PDF, etc.)

        render() can take arbitrary keyword parameters which will be
        filled in from the request (in that case they *must* be
        present in the request)."""

    def __call__():
        """This is the main method called by Zope to render the
        view. You can use that method if you whish to render the
        view."""


class ITemplateFileFactory(Interface):
    """Utility that generates templates from files in template directories.
    """

    def __call__(filename, _prefix=None):
        """Creates an ITemplate from a file

        _prefix is the directory the file is located in
        """

class ITemplate(Interface):
    """Template objects
    """

    def _initFactory(factory):
        """Template language specific initializations on the view factory."""

    def render(view):
        """Renders the template"""
