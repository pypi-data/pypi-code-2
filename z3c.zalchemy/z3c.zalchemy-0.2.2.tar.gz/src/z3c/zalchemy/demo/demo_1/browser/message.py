import zope.traversing.browser
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib.namedtemplate import NamedTemplateImplementation
from zope.formlib import form
from z3c.zalchemy.demo.demo_1.interfaces import IHelloWorldMessage
from z3c.zalchemy.demo.demo_1.message import HelloWorldMessage

from z3c.zalchemy.i18n import _

# class that defines the add form fields
class AddHelloWorldMessage(form.AddForm):

    form_fields = form.FormFields(IHelloWorldMessage).omit('__parent__')

    def create(self, data):
        return HelloWorldMessage(**data)

# class that defines the edit form fields
class EditHelloWorldMessage(form.EditForm):

    form_fields = form.FormFields(IHelloWorldMessage).omit('__parent__')

    actions = form.EditForm.actions.copy()

    @form.action(_("Apply and View"))
    def handle_edit_view_action(self, action, data):
        self.actions['form.actions.apply'].success(data)
        url = zope.traversing.browser.absoluteURL(self.context, self.request)
        self.request.response.redirect(url)

# the template for the default view
view_template = NamedTemplateImplementation(
    ViewPageTemplateFile('view.pt'))
