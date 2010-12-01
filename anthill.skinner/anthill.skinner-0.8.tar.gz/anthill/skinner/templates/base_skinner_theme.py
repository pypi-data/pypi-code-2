import copy
import datetime

from zopeskel.plone25_theme import Plone25Theme
from zopeskel.base import get_var

class BaseSkinnerTheme(Plone25Theme):
    _template_dir = 'base_skinner_theme'
    summary = "A Theme for Plone 4.0 based on anthill.skinner"
    required_templates = ['plone']
    use_cheetah = True

    vars = copy.deepcopy(Plone25Theme.vars)
    get_var(vars, 'namespace_package').default = 'plonetheme'
    get_var(vars, 'namespace_package').description = 'Namespace package (like plonetheme)'
    get_var(vars, 'description').default = 'An installable theme public theme for Plone 4.0'
    get_var(vars, 'skinbase').description = 'Name of the admin skin, this is the theme a logged in user sees, e.g. Intranet Theme'
        
    def pre(self, command, output_dir, vars):
        vars['timestamp'] = datetime.date.today().strftime("%Y%m%d")
        super(BaseSkinnerTheme, self).pre(command, output_dir, vars)
