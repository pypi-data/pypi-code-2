import inspect
from tw.api import JSLink, Link
from tw.forms import Form
from tw.jquery import jquery_js
from tg import request, TGController
from tg.decorators import Decoration, expose
from webhelpers.html import HTML

try:
    import json
except:
    import simplejson as json

jquery_form_js = JSLink(modname=__name__, filename='statics/jquery.form.js')
spinner_icon = Link(modname=__name__, filename='statics/spinner.gif')

def ajaxloaded(decorated):
    def display(w, *args, **kw):
        w.register_resources()
        form_id = w.__class__.__name__
        return HTML(HTML.div('', id=form_id), 
                    HTML.script(HTML.literal('''jQuery(document).ready(function() {{
jQuery('#{0}').load('{1}', {2});
}});'''.format(form_id, w.ajaxurl, json.dumps(kw)))))

    decorated._ajaxform_display = decorated.display
    decorated.javascript.extend([jquery_js, jquery_form_js])
    decorated.display = display
    return decorated

class formexpose(object):
    def __init__(self, arg, template='tgext.ajaxforms.templates.ajaxform'):
        if inspect.isclass(arg) and issubclass(arg, Form):
            self.form = arg()
        elif isinstance(arg, Form):
            self.form = arg
        self.template = template

    def decorate_func(self, decorated):
        def before_render(remainder, params, output):
            output['ajaxform'] = self.form
            output['ajaxform_id'] = self.form.__class__.__name__
            output['ajaxform_action'] = self.form.action
            output['ajaxform_spinner'] = spinner_icon
            if not output.has_key('value'):
                output['value'] = {}

        decorated = expose(self.template)(decorated)
        decoration = Decoration.get_decoration(decorated)
        decoration.register_hook('before_render', before_render)
        return decorated

    def __call__(self, decorated):
        return self.decorate_func(decorated)

def ajaxform(arg):
    def real_method(self, *args, **kw):
        return dict(value=kw)
    
    return formexpose(arg)(real_method)

