# -*- coding: utf-8 -*-
import copy
from zopeskel.base import get_var
from zopeskel.base import var

from zopeskel.plone3_buildout import Plone3Buildout

class Buildout(Plone3Buildout):
    _template_dir = 'templates/sc_buildout'
    summary = "Buildout para projetos Plone"
    help = """
    Este template cria um buildout para Plone 3 ou superior.
    Buildouts com Plone 3.1.x tendem a ser mais instaveis que as versoes mais 
    recentes devido a nao eggificacao desta versao.
    """
    pre_run_msg = """
    """
    
    post_run_msg = """
    Buildout criado.
    
    Voce deve, agora, criar um virtualenv dentro da pasta do buildout 
    e depois executar (troque desenvolvimento.cfg pelo arquivo desejado):
    
    source env/bin/activate
    python bootstrap.py -c desenvolvimento.cfg
    ./bin/buildout -c desenvolvimento.cfg
    """
    required_templates = []
    use_cheetah = True
    use_local_commands = False
    vars = copy.deepcopy(Plone3Buildout.vars)
    get_var(vars, 'plone_version').default = '4.0.2'
    get_var(vars, 'zope_password').default = 'admin'
    
    def post(self, command, output_dir, vars):
        super(Buildout, self).post(command, output_dir, vars)
    
    def pre(self, command, output_dir, vars):
        super(Buildout, self).pre(command, output_dir, vars)
        vars['plone3'] = vars['plone_version'].startswith("3")
        vars['plone31'] = vars['plone_version'].startswith("3.1")
        vars['plone4'] = vars['plone_version'].startswith("4")
        if vars['plone31']:
            vars['zope2_version'] = "2.11.4"
