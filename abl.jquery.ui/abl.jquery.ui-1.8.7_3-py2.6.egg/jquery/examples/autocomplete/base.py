from simplejson import dumps
from tg import TGController, tmpl_context, expose
from tg.decorators import with_trailing_slash
from tw.api import WidgetsList
from tw.forms import Form
from abl.jquery.ui.widgets import AutoCompleteTextField


class AutocompleteForm(Form):
    class fields(WidgetsList):
        text_1 = AutoCompleteTextField(options=dict(source='complete'))

autocomplete_form = AutocompleteForm()


class AutocompleteController(TGController):

    @expose('abl.jquery.examples.autocomplete.templates.index')
    @with_trailing_slash
    def index(self):
        tmpl_context.autocomplete_form = autocomplete_form
        return dict()


    @expose()
    def complete(self, term, **kwargs):
        suggestions = ['hello', 'world']
        suggestions.append(term)
        return dumps(suggestions)