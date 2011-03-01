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

import sys
import os
import warnings

from zope import component
from zope import interface
from zope.publisher.browser import BrowserPage
from zope.publisher.publish import mapply
from zope.pagetemplate import pagetemplate, pagetemplatefile
from zope.app.pagetemplate.engine import TrustedAppPT
from zope.app.publisher.browser import directoryresource
from zope.app.publisher.browser.pagetemplateresource import \
    PageTemplateResourceFactory

import martian.util
from grokcore.view import interfaces, util


class View(BrowserPage):
    interface.implements(interfaces.IGrokView)

    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self.__name__ = getattr(self, '__view_name__', None)

        if getattr(self, 'module_info', None) is not None:
            self.static = component.queryAdapter(
                self.request,
                interface.Interface,
                name=self.module_info.package_dotted_name
                )
        else:
            self.static = None

    @property
    def response(self):
        return self.request.response

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return

        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()
        return mapply(self.render, (), self.request)

    def _render_template(self):
        return self.template.render(self)

    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['static'] = self.static
        namespace['view'] = self
        return namespace

    def namespace(self):
        return {}

    def __getitem__(self, key):
        # This is BBB code for Zope page templates only:
        if not isinstance(self.template, PageTemplate):
            raise AttributeError("View has no item %s" % key)

        value = self.template._template.macros[key]
        # When this deprecation is done with, this whole __getitem__ can
        # be removed.
        warnings.warn("Calling macros directly on the view is deprecated. "
                      "Please use context/@@viewname/macros/macroname\n"
                      "View %r, macro %s" % (self, key),
                      DeprecationWarning, 1)
        return value


    def url(self, obj=None, name=None, data=None):
        """Return string for the URL based on the obj and name. The data
        argument is used to form a CGI query string.
        """
        if isinstance(obj, basestring):
            if name is not None:
                raise TypeError(
                    'url() takes either obj argument, obj, string arguments, '
                    'or string argument')
            name = obj
            obj = None

        if name is None and obj is None:
            # create URL to view itself
            obj = self
        elif name is not None and obj is None:
            # create URL to view on context
            obj = self.context

        if data is None:
            data = {}
        else:
            if not isinstance(data, dict):
                raise TypeError('url() data argument must be a dict.')

        return util.url(self.request, obj, name, data=data)

    def redirect(self, url):
        return self.request.response.redirect(url)

    def update(self, **kwargs):
        pass

    def render(self, **kwargs):
        pass

    render.base_method = True

# backwards compatibility. Probably not needed by many, but just in case.
# please start using grokcore.view.View again.
CodeView = View

class BaseTemplate(object):
    """Any sort of page template"""

    interface.implements(interfaces.ITemplate)

    __grok_name__ = ''
    __grok_location__ = ''

    def __repr__(self):
        return '<%s template in %s>' % (self.__grok_name__,
                                        self.__grok_location__)

    def _annotateGrokInfo(self, name, location):
        self.__grok_name__ = name
        self.__grok_location__ = location

    def _initFactory(self, factory):
        pass


class GrokTemplate(BaseTemplate):
    """A slightly more advanced page template

    This provides most of what a page template needs and is a good base for
    writing your own page template"""

    def __init__(self, string=None, filename=None, _prefix=None):

        # __grok_module__ is needed to make defined_locally() return True for
        # inline templates
        # XXX unfortunately using caller_module means that care must be taken
        # when GrokTemplate is subclassed. You can not do a super().__init__
        # for example.
        self.__grok_module__ = martian.util.caller_module()

        if not (string is None) ^ (filename is None):
            raise AssertionError(
                "You must pass in template or filename, but not both.")

        if string:
            self.setFromString(string)
        else:
            if _prefix is None:
                module = sys.modules[self.__grok_module__]
                _prefix = os.path.dirname(module.__file__)
            self.setFromFilename(filename, _prefix)

    def __repr__(self):
        return '<%s template in %s>' % (self.__grok_name__,
                                        self.__grok_location__)

    def _annotateGrokInfo(self, name, location):
        self.__grok_name__ = name
        self.__grok_location__ = location

    def _initFactory(self, factory):
        pass

    def namespace(self, view):
        # By default use the namespaces that are defined as the
        # default by the view implementation.
        return view.default_namespace()

    def getNamespace(self, view):
        namespace = self.namespace(view)
        namespace.update(view.namespace())
        return namespace


class TrustedPageTemplate(TrustedAppPT, pagetemplate.PageTemplate):
    pass


class TrustedFilePageTemplate(TrustedAppPT, pagetemplatefile.PageTemplateFile):
    pass


class PageTemplate(GrokTemplate):

    def setFromString(self, string):
        zpt = TrustedPageTemplate()
        if martian.util.not_unicode_or_ascii(string):
            raise ValueError("Invalid page template. Page templates must be "
                             "unicode or ASCII.")
        zpt.write(string)
        self._template = zpt

    def setFromFilename(self, filename, _prefix=None):
        self._template = TrustedFilePageTemplate(filename, _prefix)

    def _initFactory(self, factory):
        def _get_macros(self):
            return self.template._template.macros
        # _template.macros is a property that does template reloading in debug
        # mode.  A direct "factory.macros = macros" basically caches the
        # template.  So we use a property.
        factory.macros = property(_get_macros)

    def render(self, view):
        namespace = self.getNamespace(view)
        template = self._template
        namespace.update(template.pt_getContext())
        return template.pt_render(namespace)

class PageTemplateFile(PageTemplate):
    # For BBB
    def __init__(self, filename, _prefix=None):
        self.__grok_module__ = martian.util.caller_module()
        if _prefix is None:
            module = sys.modules[self.__grok_module__]
            _prefix = os.path.dirname(module.__file__)
        self.setFromFilename(filename, _prefix)


class DirectoryResource(directoryresource.DirectoryResource):
    # We subclass this, because we want to override factories for
    # .pt and .html file types, not creating pagetemplate resources.
    resource_factories = {}
    for type, factory in (directoryresource.DirectoryResource.
                          resource_factories.items()):
        if factory is PageTemplateResourceFactory:
            continue
        resource_factories[type] = factory

    # Hook for our own DirectoryResourceFactory. Can only be set *after*
    # having defined the DirectoryResourceFactory class.
    directory_factory = None


class DirectoryResourceFactory(directoryresource.DirectoryResourceFactory):
    # We need this to allow hooking up our own DirectoryResource class.
    factoryClass = DirectoryResource


DirectoryResource.directory_factory = DirectoryResourceFactory
