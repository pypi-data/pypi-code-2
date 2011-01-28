##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import warnings

import zope.interface
import zope.component
import zope.schema

from zope.publisher.browser import BrowserPage
from zope.security.proxy import removeSecurityProxy
import zope.component.interfaces
import zope.publisher.interfaces.browser

import zope.app.pagetemplate
from zope.app.component.browser.registration import IRegistrationDisplay
from zope.app.component.browser.registration import ISiteRegistrationDisplay

from z3c.template.template import getPageTemplate
from z3c.formui import form
from z3c.form import field
from z3c.form import button
from z3c.pagelet import browser

from zam.api.i18n import MessageFactory as _


def _registrations(context, comp):
    sm = zope.component.getSiteManager(context)
    for r in sm.registeredUtilities():
        if r.component == comp or comp is None:
            yield r
    for r in sm.registeredAdapters():
        if r.factory == comp or comp is None:
            yield r
    for r in sm.registeredSubscriptionAdapters():
        if r.factory == comp or comp is None:
            yield r
    for r in sm.registeredHandlers():
        if r.factory == comp or comp is None:
            yield r


class RegistrationView(browser.BrowserPagelet):

    zope.component.adapts(None, zope.publisher.interfaces.browser.IBrowserRequest)

    template = getPageTemplate()

    def registrations(self):
        registrations = [
            zope.component.getMultiAdapter((r, self.request), IRegistrationDisplay)
            for r in sorted(_registrations(self.context, self.context))
            ]
        return registrations

    def update(self):
        registrations = dict([(r.id(), r) for r in self.registrations()])
        for id in self.request.form.get('ids', ()):
            r = registrations.get(id)
            if r is not None:
                r.unregister()

    def render(self):
        return self.template()


class UtilityRegistrationDisplay(object):
    """Utility Registration Details"""

    zope.component.adapts(zope.component.interfaces.IUtilityRegistration,
                     zope.publisher.interfaces.browser.IBrowserRequest)
    zope.interface.implements(IRegistrationDisplay)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def provided(self):
        provided = self.context.provided
        return provided.__module__ + '.' + provided.__name__

    def id(self):
        return 'R' + (("%s %s" % (self.provided(), self.context.name))
                      .encode('utf8')
                      .encode('base64')
                      .replace('+', '_')
                      .replace('=', '')
                      .replace('\n', '')
                      )

    def _comment(self):
        comment = self.context.info or ''
        if comment:
            comment = _("comment: ${comment}", mapping={"comment": comment})
        return comment

    def _provided(self):
        name = self.context.name
        provided = self.provided()
        if name:
            info = _("${provided} utility named '${name}'",
                     mapping={"provided": provided, "name": name})
        else:
            info = _("${provided} utility",
                     mapping={"provided": provided})
        return info

    def render(self):
        return {
            "info": self._provided(),
            "comment": self._comment()
            }

    def unregister(self):
        self.context.registry.unregisterUtility(
            self.context.component,
            self.context.provided,
            self.context.name,
            )


class SiteRegistrationView(RegistrationView):

    def registrations(self):
        registrations = [
            zope.component.getMultiAdapter((r, self.request),
                                      ISiteRegistrationDisplay)
            for r in sorted(_registrations(self.context, None))
            ]
        return registrations


class UtilitySiteRegistrationDisplay(UtilityRegistrationDisplay):
    """Utility Registration Details"""

    zope.interface.implementsOnly(ISiteRegistrationDisplay)

    def render(self):
        url = zope.component.getMultiAdapter(
            (self.context.component, self.request), name='absolute_url')
        try:
            url = url()
        except TypeError:
            url = ""

        cname = getattr(self.context.component, '__name__', '')
        if not cname:
            cname = _("(unknown name)")
        if url:
            url += "/@@SelectedManagementView.html"

        return {
            "cname": cname,
            "url": url,
            "info": self._provided(),
            "comment": self._comment()
            }


class AddUtilityRegistration(form.Form):
    """View for registering utilities

    Normally, the provided interface and name are input.

    A subclass can provide an empty 'name' attribute if the component should
    always be registered without a name.

    A subclass can provide a 'provided' attribute if a component
    should always be registered with the same interface.

    """
    zope.component.adapts(None, zope.publisher.interfaces.browser.IBrowserRequest)

    formErrorsMessage = _('There were some errors.')
    ignoreContext = True

    fields = field.Fields(
        zope.schema.Choice(
           __name__ = 'provided',
           title=_("Provided interface"),
           description=_("The interface provided by the utility"),
           vocabulary="Utility Component Interfaces",
           required=True,
           ),
        zope.schema.TextLine(
           __name__ = 'name',
           title=_("Register As"),
           description=_("The name under which the utility will be known."),
           required=False,
           default=u'',
           missing_value=u''
           ),
        zope.schema.Text(
           __name__ = 'comment',
           title=_("Comment"),
           required=False,
           default=u'',
           missing_value=u''
           ),
        )

    name = provided = None

    prefix = 'field' # in hopes of making old tests pass. :)

    def __init__(self, context, request):
        if self.name is not None:
            self.fields = self.fields.omit('name')
        if self.provided is not None:
            self.fields = self.fields.omit('provided')
        super(AddUtilityRegistration, self).__init__(context, request)

    @property
    def label(self):
        return _("Register a $classname",
                 mapping=dict(classname=self.context.__class__.__name__)
                 )

    @button.buttonAndHandler(_('Register'), name='register')
    def handleRegister(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        sm = zope.component.getSiteManager(self.context)
        name = self.name
        if name is None:
            name = data['name']
        provided = self.provided
        if provided is None:
            provided = data['provided']

        # We have to remove the security proxy to save the registration
        sm.registerUtility(
            removeSecurityProxy(self.context),
            provided, name,
            data['comment'] or '')

        self.request.response.redirect('@@registration.html')
