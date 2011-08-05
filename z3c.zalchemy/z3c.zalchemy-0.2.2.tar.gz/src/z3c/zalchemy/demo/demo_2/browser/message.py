import zope.traversing.browser
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib.namedtemplate import NamedTemplateImplementation
from zope.formlib import form
from z3c.zalchemy.demo.demo_2.interfaces import IHelloWorldMessage2
from z3c.zalchemy.demo.demo_2.message import HelloWorldMessage2

from z3c.zalchemy.i18n import _

#Define the schema for the message ad form
class AddHelloWorldMessage(form.AddForm):

    form_fields = form.FormFields(IHelloWorldMessage2).omit('__parent__')

    def create(self, data):
        return HelloWorldMessage2(**data)

# Define the schema for the messag edit form
class EditHelloWorldMessage(form.EditForm):

    form_fields = form.FormFields(IHelloWorldMessage2).omit('__parent__')

    actions = form.EditForm.actions.copy()

    @form.action(_("Apply and View"))
    def handle_edit_view_action(self, action, data):
        self.actions['form.actions.apply'].success(data)
        url = zope.traversing.browser.absoluteURL(self.context, self.request)
        self.request.response.redirect(url)

# The template used for the default index.html view
view_template = NamedTemplateImplementation(
    ViewPageTemplateFile('view.pt'))
