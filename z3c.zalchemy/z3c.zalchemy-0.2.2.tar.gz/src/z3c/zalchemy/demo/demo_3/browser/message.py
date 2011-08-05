import zope.traversing.browser
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib.namedtemplate import NamedTemplateImplementation
from zope.formlib import form
from z3c.zalchemy.demo.demo_3.interfaces import IHelloWorldMessage3
from z3c.zalchemy.demo.demo_3.message import HelloWorldMessage3
from zope.dublincore.interfaces import IZopeDublinCore

from z3c.zalchemy.i18n import _

class AddHelloWorldMessage3(form.AddForm):

    form_fields = form.FormFields(IZopeDublinCore).select('title', 'description')+form.FormFields(IHelloWorldMessage3).omit('__parent__')

    def create(self, data):
        return HelloWorldMessage3(**data)

class EditHelloWorldMessage3(form.EditForm):

    form_fields = form.FormFields(IZopeDublinCore).select('title', 'description')+form.FormFields(IHelloWorldMessage3).omit('__parent__')

    actions = form.EditForm.actions.copy()

    @form.action(_("Apply and View"))
    def handle_edit_view_action(self, action, data):
        self.actions['form.actions.apply'].success(data)
        url = zope.traversing.browser.absoluteURL(self.context, self.request)
        self.request.response.redirect(url)

view_template = NamedTemplateImplementation(
    ViewPageTemplateFile('view.pt'))
