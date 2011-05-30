# -*- coding: utf-8 -*-
import copy
from zopeskel.base import get_var
from zopeskel.base import var

from zopeskel.plone_app import PloneApp

class Package(PloneApp):
    _template_dir = 'templates/portal_package'
    summary = "Package usado em projetos Plone"
    required_templates = ['plone_app']
    use_cheetah = True
    use_local_commands = True
    vars = copy.deepcopy(PloneApp.vars)
    get_var(vars, 'namespace_package').default = 'sc'
    get_var(vars, 'namespace_package').description = 'Namespace principal (sempre sc)'
    get_var(vars, 'namespace_package2').default = 's17'
    get_var(vars, 'namespace_package2').description = 'Usualmente o nome base do produto'
    get_var(vars, 'package').default = 'bookshelf'
    get_var(vars, 'package').description = 'Nome do produto'   
    get_var(vars, 'version').default = '0.5'
    get_var(vars, 'author').default = 'Simples Consultoria'
    get_var(vars, 'author_email').default = 'products@simplesconsultoria.com.br'
    get_var(vars, 'url').default = 'http://www.simplesconsultoria.com.br/'

    def pre(self, command, output_dir, vars):  
        vars['package_dotted_name'] = vars['namespace_package'] + '.' + vars['namespace_package2'] + '.' + vars['package']
    
    def post(self, command, output_dir, vars):
        super(Package, self).pre(command, output_dir, vars)
