import tg
from tg import request, config
from tg.decorators import use_custom_format, Decoration

class expose_mobile(object):
    def __init__(self, template, content_type='text/html'):
        if template in config.get('renderers', []):
            engine, template = template, ''
        elif ':' in template:
            engine, template = template.split(':', 1)
        elif template:
            engine = config.get('default_renderer')
        else:
            engine, template = None, None

        self.template = template
        self.engine = engine
        self.content_type = content_type

    def hook_func(self, *args, **kwargs):
        if request.is_mobile:
            use_custom_format(self.func, 'mobile')
        else:
            #currently turbogears needs to reset the custom_format at each request or it will
            #use the last requested custom format for every request.
            deco = Decoration.get_decoration(self.func)
            deco.render_custom_format = None

    def __call__(self, func):
        self.func = func
        deco = Decoration.get_decoration(func)
        deco.register_custom_template_engine('mobile', self.content_type, self.engine, self.template, [])
        deco.register_hook('before_render', self.hook_func)
        return func
