# -*- coding: utf-8 -*-
# $Id: browser.py 237778 2011-04-18 10:40:52Z glenfant $
"""Views for the control panel"""
from urllib import quote_plus
from zope.schema import getFieldsInOrder
from Products.Five.browser import BrowserView

NO_NAMESPACE = '(No namespace)'

class ZMIView(BrowserView):


    def namespaces(self):
        """List of mappings with keys :
        - 'namespace_url'
        - 'view_url'
        """
        out = []
        namespaces= self.context.getNamespaces().keys()
        namespaces.sort()
        for namespace in namespaces:
            if namespace == '':
                namespace = NO_NAMESPACE
            features = {
                'namespace_url': namespace,
                'view_url': '@@view_namespace?ns=' + quote_plus(namespace)
                }
            out.append(features)
        return out

    def this_namespace(self):
        """URL of actually focused namespace
        """
        return self.request.form.get('ns')


    def this_namespace_view_url(self):
        return '@@view_namespace?ns=%s' % quote_plus(self.this_namespace())


    def this_directive(self):
        """Name of actually focused directive
        """
        return self.request.form.get('directive')


    def this_directive_view_url(self):
        return '@@view_directive?ns=%s&directive=%s' % (
               quote_plus(self.this_namespace()), self.this_directive())


    def this_subdirective(self):
        """Name of actually focused directive
        """
        return self.request.form.get('subdir')


    def list_directives(self):
        """Enumerates sorted directives for this_namespace as mappings with keys :
        - 'name'
        - 'view_url'
        """
        out = []
        this_namespace = self.this_namespace()
        if this_namespace == NO_NAMESPACE:
            this_namespace = ''
        directives = self.context.getNamespaces()[this_namespace].keys()
        directives.sort()
        for directive in directives:
            features = {
                'name': directive,
                'view_url': '@@view_directive?ns=%s&directive=%s' % (
                             quote_plus(self.this_namespace()), directive)
                }
            out.append(features)
        return out


    def directive_infos(self):
        """Provide ZPT friendly data to display a directive documentation
        """
        this_namespace = self.this_namespace()
        if this_namespace == NO_NAMESPACE:
            this_namespace = ''
        this_directive = self.this_directive()
        schema, handler, zcml_source = self.context.getNamespaces()[this_namespace][this_directive]
        return DirectiveInfos(schema, handler, zcml_source)


    def list_subdirectives(self):
        """Provide links to potential subdirectives as mappings with keys:
        - 'name'
        - 'view_url'
        """
        out = []
        this_namespace = self.this_namespace()
        if this_namespace == NO_NAMESPACE:
            this_namespace = ''
        this_directive = self.this_directive()
        key = (this_namespace, this_directive)
        subdirs = self.context.getSubdirs().get(key, [])
        for namespace, name, schema, handler, zcml_source in subdirs:
            features = {
                'name': name,
                'view_url': '@@view_subdirective?ns=%s&directive=%s&subdir=%s' % (
                            quote_plus(namespace), this_directive, name)
                }
            out.append(features)
        return out


    def subdirective_infos(self):
        """Provide ZPT friendly data to display a directive documentation
        """
        this_namespace = self.this_namespace()
        if this_namespace == NO_NAMESPACE:
            this_namespace = ''
        this_directive = self.this_directive()
        this_subdirective = self.this_subdirective()
        key = (this_namespace, this_directive)
        subdirs = self.context.getSubdirs().get(key, [])
        for namespace, name, schema, handler, zcml_source in subdirs:
            if name == self.this_subdirective():
                # We will always find
                break
        return DirectiveInfos(schema, handler, zcml_source)


class DirectiveInfos(object):

    def __init__(self, schema, handler, zcml_source):
        self._schema = schema
        self._handler = handler
        self._zcml_source = zcml_source
        return

    def summary(self):
        """Text summary of the directive
        FIXME: may be in rst
        """
        summary = self._schema.getDoc()
        if summary.strip() == '':
            summary = "(not available)"
        return summary

    def attributes(self):
        """ZPT friendly list of directive attributes as mappings with keys:
        - name
        - title
        - description
        - option
        - type
        """
        out = []
        for name, field in getFieldsInOrder(self._schema):
            name = name.strip('_')
            if field.required:
                option = 'Required'
            else:
                option = 'Optional, default=%s' % repr(field.default)
            atype = field.__class__.__name__
            features = {
                'name': name,
                'title': field.title,
                'option': option,
                'type': field.__class__.__name__,
                'description': field.description
                }
            out.append(features)
        return out

    def zcml_source(self):
        """File and lines of ZCML definition
        """
        return repr(self._zcml_source)

    def python_handler(self):
        """Dotted name of the function/method that handles this directive
        """
        if self._handler is not None:
            return self._handler.__module__ + '.' + self._handler.__name__
        else:
            return '(No handler)'
