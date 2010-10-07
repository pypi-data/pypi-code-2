# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: meta.py 42404 2010-05-26 17:13:48Z sylvain $

from App.class_init import InitializeClass as initializeClass
from Products.Five.security import protectName

from five import grok
from martian.error import GrokError
from zope import interface, component
import martian

from infrae.rest.components import REST, ALLOWED_REST_METHODS
from infrae.rest.interfaces import IRESTLayer


def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()


class RESTGrokker(martian.ClassGrokker):
    """Grok REST views.
    """
    martian.component(REST)
    martian.directive(grok.context)
    martian.directive(grok.name, get_default=default_view_name)
    martian.directive(grok.require, name='permission')

    def execute(self, factory, context, name, permission, config, **kw):
        """Register the REST component as a view on the IREST layer.
        """
        if permission is None:
            permission = 'zope.Public'
        method_defined = False
        for method in ALLOWED_REST_METHODS:
            if hasattr(factory, method):
                method_defined = True
        if not method_defined:
            raise GrokError(
                "REST component %s doesn't define any REST method" % (name,),
                factory)

        adapts = (context, IRESTLayer)
        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(factory, adapts, interface.Interface, name))

        for method in ALLOWED_REST_METHODS:
            if hasattr(factory, method):
                config.action(
                    discriminator = ('five:protectName', factory, method),
                    callable = protectName,
                    args = (factory, method, permission))

        config.action(
            discriminator = ('five:initialize:class', factory),
            callable = initializeClass,
            args = (factory,))
        return True
