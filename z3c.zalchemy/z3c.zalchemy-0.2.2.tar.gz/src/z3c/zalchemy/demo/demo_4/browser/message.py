import zope.traversing.browser
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib.namedtemplate import NamedTemplateImplementation
from zope.formlib import form
from z3c.zalchemy.demo.demo_4.interfaces import IHelloWorldMessage4, IHelloWorldFragment
from z3c.zalchemy.demo.demo_4.message import HelloWorldMessage4, HelloWorldFragment
from zope.dublincore.interfaces import IZopeDublinCore

from z3c.zalchemy.i18n import _

class AddHelloWorldMessage(form.AddForm):

    form_fields = form.FormFields(IZopeDublinCore).select('title', 'description')+form.FormFields(IHelloWorldMessage4).omit('__parent__','className')

    def create(self, data):
        return HelloWorldMessage4(**data)

class EditHelloWorldMessage(form.EditForm):

    form_fields = form.FormFields(IZopeDublinCore).select('title', 'description')+form.FormFields(IHelloWorldMessage4).omit('__parent__','className')

    actions = form.EditForm.actions.copy()

    @form.action(_("Apply and View"))
    def handle_edit_view_action(self, action, data):
        self.actions['form.actions.apply'].success(data)
        url = zope.traversing.browser.absoluteURL(self.context, self.request)
        self.request.response.redirect(url)

class AddHelloWorldFragment(form.AddForm):

    form_fields = form.FormFields(IHelloWorldFragment).omit('__parent__')

    def create(self, data):
        return HelloWorldFragment(**data)

class EditHelloWorldFragment(form.EditForm):

    form_fields = form.FormFields(IHelloWorldFragment).omit('__parent__')

    actions = form.EditForm.actions.copy()

    @form.action(_("Apply and View"))
    def handle_edit_view_action(self, action, data):
        self.actions['form.actions.apply'].success(data)
        url = zope.traversing.browser.absoluteURL(self.context, self.request)
        self.request.response.redirect(url)

view_template = NamedTemplateImplementation(
    ViewPageTemplateFile('view.pt'))
