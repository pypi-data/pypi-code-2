from formencode.validators import NotEmpty
from tg import (
    TGController,
    expose,
    validate,
)
from tg import tmpl_context as c
from tg.decorators import with_trailing_slash
from tw.api import WidgetsList
from tw.forms import (
    TableForm,
    TextField,
)
from abl.jquery.core.widgets import AjaxUpdateContentWidget
from abl.jquery.plugins.form.widgets import (
    AjaxFormMixin,
    AjaxFormUpdateMixin,
)


class MyForm(TableForm, AjaxFormMixin):
    class children(WidgetsList):
        text = TextField(validator=NotEmpty())


class MyUpdateForm(TableForm, AjaxFormUpdateMixin):
    class children(WidgetsList):
        text = TextField(validator=NotEmpty())

my_form = MyForm('my_form',
                 action="submit/")

my_update_form = MyUpdateForm('my_update_form',
                              action="submit_update/")

#Not required, but nice if you want to reload the form again
#So this example also illustrates how to update content
update_widget = AjaxUpdateContentWidget('update_widget')


class FormController(TGController):

    @expose('abl.jquery.examples.form.templates.index')
    @with_trailing_slash
    def index(self, **kwargs):
        c.my_form = my_form
        c.my_update_form = my_update_form
        c.update_widget = update_widget
        return dict()


    @expose("abl.jquery.plugins.form.templates.error_handler")
    def submit_error_handler(self, **kwargs):
        c.form = my_form
        return dict()


    @expose("abl.jquery.examples.form.templates.submit")
    @with_trailing_slash
    @validate(form=my_form, error_handler=submit_error_handler)
    def submit(self, text):
        return dict(text=text)


    @expose("abl.jquery.core.templates.update_content")
    @with_trailing_slash
    def get_form(self):
        #use a generic update_content template here
        #it iterates over the content dict
        #formbox is the container of the form, see index.html
        return dict(content=dict(formbox=my_form()))


    @expose("abl.jquery.plugins.form.templates.error_handler")
    def submit_update_error_handler(self, **kwargs):
        c.form = my_update_form
        return dict()


    @expose("abl.jquery.core.templates.update_content")
    @with_trailing_slash
    @validate(form=my_update_form, error_handler=submit_update_error_handler)
    def submit_update(self, text):
        #not only returning html but multiple containers
        return dict(content=dict(formbox2=my_update_form(),
                                 result=text))