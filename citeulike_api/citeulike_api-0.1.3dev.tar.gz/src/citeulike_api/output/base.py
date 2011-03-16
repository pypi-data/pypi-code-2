# -*- coding: utf-8 -*-
from jinja2 import Environment, PackageLoader
# from jinja2 import Template
# template = Template('Hello {{ name }}!')
# >>> template.render(name='John Doe')
# u'Hello John Doe!'

class BaseRenderer(object):
    """Common base-class for renderers."""
    
    def __init__(self,
          template_name=None,
          env_args=None,
          *args, **kwargs):
        if template_name is not None:
            self.template_name = template_name
        # env_args.setdefault(
        if env_args is None:
            env_args={}
        env = Environment(
          loader=PackageLoader('citeulike', 'templates',),
          **env_args)
        self.env = env
    
    def get_template(self, template_name=None):
        if not template_name:
            template_name = self.template_name
        return self.env.get_template(template_name)
    
    def render(self, record_list, *args, **kwargs):
        return self.get_template().render(
          record_list=record_list, *args, **kwargs)