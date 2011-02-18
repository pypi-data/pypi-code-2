from formencode.validators import NotEmpty
from tg import (
    TGController,
    expose,
    tmpl_context,
    validate,
)
from tg.decorators import with_trailing_slash
from tw.api import WidgetsList
from tw.forms import (
    TableForm,
    TextField,
)
from abl.jquery.ui.widgets import (
    DialogContentWidget,
    DialogConfirmWidget,
    DialogFormWidget,
)


class MyForm(TableForm):
    #Don't need a submit button because its provided by the dialog
    submit_text = None

    class fields(WidgetsList):
        text = TextField("text",
                         validator=NotEmpty())
        more_text = TextField("more_text")


my_form = MyForm(action='dialog_action/')

dialog_content_widget = DialogContentWidget('dialog_content_widget')

dialog_content_widget2 = DialogContentWidget('dialog_content_widget2',
                                             url='content2',
                                             title='widget gave me a title')

dialog_confirm_widget = DialogConfirmWidget('dialog_confirm_widget',
                                            action_url="confirm_action",
                                            button_confirm="Confirm",
                                            config=dict(width=400))

dialog_form_widget = DialogFormWidget('dialog_form_widget',
                                      submit_button="Submit Form",
                                      config=dict(width=600))


class DialogController(TGController):

    @expose('abl.jquery.examples.dialog.templates.index')
    @with_trailing_slash
    def index(self):
        tmpl_context.dialog_content_widget = dialog_content_widget
        tmpl_context.dialog_content_widget2 = dialog_content_widget2
        tmpl_context.dialog_confirm_widget = dialog_confirm_widget
        tmpl_context.dialog_form_widget = dialog_form_widget
        return dict()


    @expose()
    @with_trailing_slash
    def content(self):
        return "content for the dialog"


    @expose()
    @with_trailing_slash
    def content2(self):
        return "another content for the dialog"


    @expose()
    @with_trailing_slash
    def confirm_action(self):
        return "the confirm action"


    @expose("abl.jquery.examples.dialog.templates.my_form")
    @with_trailing_slash
    def dialog_form_content(self, **kwargs):
        tmpl_context.my_form = my_form
        return dict()


    @expose("abl.jquery.examples.dialog.templates.new_content")
    @with_trailing_slash
    @validate(form=my_form, error_handler=dialog_form_content)
    def dialog_action(self, text, more_text):
        return dict(text=text,
                    more_text=more_text)

