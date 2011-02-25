# -*- coding: utf-8 -*-
import copy
from zopeskel.base import get_var
from zopeskel.base import var

from zopeskel.plone_app import PloneApp

class Policy(PloneApp):
    _template_dir = 'templates/portal_policy'
    summary = "Portal Policy para projetos Plone"
    required_templates = ['plone_app']
    use_cheetah = True
    use_local_commands = False
    vars = copy.deepcopy(PloneApp.vars)
    get_var(vars, 'namespace_package').default = 'sc'
    get_var(vars, 'namespace_package').description = 'Namespace principal (sempre sc)'
    get_var(vars, 'namespace_package2').default = 'diaspar'
    get_var(vars, 'namespace_package2').description = 'Usualmente o nome do cliente'
    get_var(vars, 'package').default = 'portal'
    get_var(vars, 'package').description = 'Nome do projeto'   
    get_var(vars, 'version').default = '0.5'
    get_var(vars, 'author').default = 'Simples Consultoria'
    get_var(vars, 'author_email').default = 'products@simplesconsultoria.com.br'
    get_var(vars, 'url').default = 'http://www.simplesconsultoria.com.br/'
    
    def post(self, command, output_dir, vars):
        super(Policy, self).pre(command, output_dir, vars)
