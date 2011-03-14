import copy

from zopeskel.plone import BasicZope
from zopeskel.base import get_var
from zopeskel.base import var

class Theme(BasicZope):
    _template_dir = 'templates/gomobile_theme'
    summary = "A theme for Go Mobile for Plone"
    help = """
"""
    category = "Plone Development"
    required_templates = ['basic_namespace']
    use_local_commands = True
    use_cheetah = True
    vars = copy.deepcopy(BasicZope.vars)

    
    
    get_var(vars, 'namespace_package').default = 'gomobiletheme'
    get_var(vars, 'package').default = 'yourcompany'
    get_var(vars, 'description').default = 'A theme for Go mobile for Plone'


            
