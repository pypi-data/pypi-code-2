# -*- coding: utf-8 -*-
import os
import copy
from paste.script import templates
from zopeskel.base import update_setup_cfg
from zopeskel.base import get_var
from zopeskel.base import var

from zopeskel.plone_app import PloneApp

class Package(PloneApp):
    _template_dir = 'templates/portal_package'
    summary = "Simples Consultoria's skeleton for a package to be used in Plone."
    required_templates = ['plone_app']
    category = "Plone Development"
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
        # Remove tests.py -- we already have a tests/ package
        path = os.path.join(output_dir,
                            vars['namespace_package'],
                            vars['namespace_package2'],
                            vars['package'])
        os.remove(os.path.join(path, 'tests.py'))
    
    def check_vars(self, vars, cmd):
        response = super(Package,self).check_vars(vars,cmd)
        self.response = copy.deepcopy(response)
        return response
    
    def run(self, command, output_dir, vars):
        ''' Override run method to avoid losing our default values'''
        if self.use_local_commands and 'ZopeSkel' not in self.egg_plugins:
            self.egg_plugins.append('ZopeSkel')
        
        vars.update(self.response)
        templates.Template.run(self, command, output_dir, vars)
        setup_cfg = os.path.join(output_dir, 'setup.cfg')
        if self.use_local_commands:
            update_setup_cfg(setup_cfg, 'zopeskel', 'template', self.name)
        
    

