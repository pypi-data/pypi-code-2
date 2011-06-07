import re
from django.template import Template, TemplateDoesNotExist
from django.template.loader import make_origin, BaseLoader


DEFAULT_PATTERNS =     {
        'jinja2': re.compile('jinja2\.html?$'),
        'mako': re.compile('mako\.html?$'),
        'hamlpy': re.compile('\.hamlpy$')
    }
patterns = DEFAULT_PATTERNS

def digg_dict_from_context(context):
    context_dict = {}
    for d in context.dicts:
        context_dict.update(d)
    return context_dict


templates = []


try:
    from jinja2 import Template as _Jinja2Template
    class Jinja2Template(_Jinja2Template):
        def render(self, context):
            context_dict = digg_dict_from_context(context)
            return super(Jinja2Template, self).render(context_dict)
    templates.append(('jinja2', Jinja2Template))
except ImportError:
    pass


try:
    from mako.template import Template as _MakoTemplate
    class MakoTemplate(_MakoTemplate):
        def render(self, context):
            context_dict = digg_dict_from_context(context)
            return super(MakoTemplate, self).render(**context_dict)
    templates.append(('mako', MakoTemplate))
except ImportError:
    pass


try:
    from hamlpy.hamlpy import Compiler as _HamlPyCompiler
    def is_hamlpy(template_name):
        return bool(patterns['hamlpy'].search(template_name))
except ImportError:
    is_hamlpy = lambda x: False


class BaseLoaderMonkeyPatched(BaseLoader):
    def load_template(self, template_name, template_dirs=None):
        source, display_name = self.load_template_source(template_name, template_dirs)
        origin = make_origin(display_name, self.load_template_source, template_name, template_dirs)
        template = None
        try:
            if is_hamlpy(template_name):
                compiler = _HamlPyCompiler()
                source = compiler.process_lines(source)
            else:
                for key, klass in templates:
                    if patterns[key].search(template_name):
                        template = klass(source)
                        break
            if template is None:
                template = Template(source)
            return template, None
        except TemplateDoesNotExist:
            return source, display_name
