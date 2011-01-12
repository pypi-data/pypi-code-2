# -*- coding: utf-8 -*-
import os

import grokcore.component as grok
import grokcore.formlib
import grokcore.message
import grokcore.view
import zope.component

from megrok.layout.interfaces import IPage, ILayout
from zope.interface import Interface
from zope.publisher.publish import mapply
from zope.component.hooks import getSite


class UtilityView(object):
    """A view mixin with useful methods.
    """

    def application_url(self, name=None):
        """Return the URL of the nearest site.
        """
        site = getSite()
        if site is None:
            raise zope.component.ComponentLookupError("No site found.")
        return self.url(site, name)

    def flash(self, message, type='message'):
        """Sends a message to the session messager.
        """
        return grokcore.message.send(message, type)


class Layout(grokcore.view.ViewSupport, UtilityView):
    """A layout object.
    """
    grok.baseclass()
    grok.implements(ILayout)

    def __init__(self, request, context):
        self.context = context
        self.request = request
        self.view = None

        if getattr(self, 'module_info', None) is not None:
            self.static = zope.component.queryAdapter(
                self.request, Interface,
                name=self.module_info.package_dotted_name)
        else:
            self.static = None

    def default_namespace(self):
        namespace = {}
        namespace['view'] = self.view
        namespace['layout'] = self
        namespace['static'] = self.static
        namespace['context'] = self.context
        namespace['request'] = self.request
        return namespace

    def namespace(self):
        return {}

    def update(self):
        pass

    def _render_template(self):
        return self.template.render(self)

    def render(self):
        return self._render_template()

    render.base_method = True

    def __call__(self, view):
        self.view = view
        self.update()
        return self.render()


class Page(grokcore.view.View, UtilityView):
    """A view class.
    """
    grok.baseclass()
    grok.implements(IPage)

    def __init__(self, context, request):
        super(Page, self).__init__(context, request)
        self.layout = None

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return
        self.layout = zope.component.getMultiAdapter(
            (self.request, self.context), ILayout)
        return self.layout(self)

    def default_namespace(self):
        namespace = super(Page, self).default_namespace()
        namespace['layout'] = self.layout
        return namespace

    def content(self):
        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()
        return mapply(self.render, (), self.request)


class LayoutAwareForm(UtilityView):
    """A mixin to make form aware of layouts.
    """

    def __init__(self, context, request):
        super(LayoutAwareForm, self).__init__(context, request)
        self.layout = None

    def default_namespace(self):
        namespace = super(LayoutAwareForm, self).default_namespace()
        namespace['layout'] = self.layout
        return namespace

    def content(self):
        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()
        return mapply(self.render, (), self.request)

    def __call__(self):
        """Calls update and returns the layout template which calls render.
        """
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return

        self.update_form()
        if self.request.response.getStatus() in (302, 303):
            return

        self.layout = zope.component.getMultiAdapter(
            (self.request, self.context), ILayout)
        return self.layout(self)


# Default forms for form without the html and body tags
default_form_template = grokcore.view.PageTemplateFile(
    os.path.join('templates', 'default_edit_form.pt'))
default_form_template.__grok_name__ = 'default_edit_form'

default_display_template = grokcore.view.PageTemplateFile(
    os.path.join('templates', 'default_display_form.pt'))
default_display_template.__grok_name__ = 'default_display_form'

grokcore.view.templatedir('templates')


class Form(LayoutAwareForm, grokcore.formlib.Form):
    """A form base class.
    """
    grok.baseclass()
    grokcore.view.template('default_form_template')


class AddForm(LayoutAwareForm, grokcore.formlib.AddForm):
    """Base add form.
    """
    grok.baseclass()
    template = default_form_template


class EditForm(LayoutAwareForm, grokcore.formlib.EditForm):
    """Base edit form.
    """
    grok.baseclass()
    template = default_form_template


class DisplayForm(LayoutAwareForm, grokcore.formlib.DisplayForm):
    """Base display form.
    """
    grok.baseclass()
    template = default_display_template
