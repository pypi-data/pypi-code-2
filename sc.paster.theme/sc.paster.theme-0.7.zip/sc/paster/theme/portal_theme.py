# -*- coding: utf-8 -*-
import copy
from zopeskel.base import get_var
from zopeskel.base import var

from zopeskel.plone_app import PloneApp

class Theme(PloneApp):
    _template_dir = 'templates/portal_theme'
    summary = "Tema visual para projetos Plone"
    required_templates = []
    use_cheetah = True
    use_local_commands = False
    vars = copy.deepcopy(PloneApp.vars)
    hide_vars = ['zip_safe','license_name','zope2product','keywords',
                 'version','author','author_email','url','long_description']
    vars = [v for v in vars if v.name not in hide_vars]
    get_var(vars, 'namespace_package').default = 'beyondskins'
    get_var(vars, 'namespace_package').description = 'Namespace principal (sempre sc)'
    get_var(vars, 'namespace_package2').default = 'diaspar'
    get_var(vars, 'namespace_package2').description = 'Usualmente o nome do cliente'
    get_var(vars, 'package').default = 'portal'
    get_var(vars, 'package').description = 'Nome do projeto'
    
    
    def pre(self,command, output_dir, vars):
        ''' Define variaveis padrao
        '''
        vars['zip_safe']=True
        vars['license_name']='GPL'
        vars['zope2product']=True
        vars['keywords']='web zope plone theme skin simples_consultoria'
        vars['version'] = '0.5'
        vars['author'] = 'Simples Consultoria'
        vars['author_email'] = 'products@simplesconsultoria.com.br'
        vars['url'] = 'http://www.simplesconsultoria.com.br/'
        vars['long_description']=''
        