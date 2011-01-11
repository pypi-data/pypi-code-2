import os
from grokproject.templates import GrokProject
from paste.script import templates


def modify_vars(vars):
    vars['install_requires'] = """
                        'zope.app.exception',
                        'zope.browserresource',
# Basic Dolmen Site
                        'dolmen.app.site',
                        'dolmen.app.layout',
                        'dolmen.app.content',
                        'dolmen.app.container',"""
    vars['additional_grants'] = """
      <grant permission="dolmen.content.View"
             principal="zope.Everybody" />""" 

    version_url = vars.get('version_url')
    if version_url is None:
        version_url = """
# anonymous sources
    http://gitweb.dolmen-project.org/misc.git?a=blob_plain;f=dolmen-kgs-1.0dev.cfg;hb=HEAD
# authenticated sources
#    http://gitweb.dolmen-project.org/misc.git?a=blob_plain;f=dolmen-kgs-dev.cfg;hb=HEAD"""
        
    vars['version_url'] = """%s
    sources.cfg""" % version_url

    vars['include_site_packages'] = """true
allowed-eggs-from-site-packages = PIL"""

    vars['run_buildout'] = 'false'

    return vars


class DolmenBasicProject(templates.Template):
    _template_dir = 'template_basic'
    summary = "A basic dolmen project"
    required_templates = ['grok']

    def check_vars(self, vars, cmd):
        vars = modify_vars(vars)
        return vars

    def post(self, command, output_dir, vars):
        os.remove(os.path.join(output_dir, 'src', vars['package'], 'app_templates', 'index.pt'))


class DolmenProject(DolmenBasicProject):
    _template_dir = 'template'
    summary = "A dolmen project"
    required_templates = ['grok']

    def check_vars(self, vars, cmd):
        vars = modify_vars(vars)
        vars['install_requires'] = """
                        'zope.app.exception',
                        'zope.browserresource',
# Basic Dolmen Site
                        'dolmen.app.site',
                        'dolmen.app.layout',
                        'dolmen.app.content',
                        'dolmen.app.container',
# PAU
                        'zope.authentication',
                        'zope.pluggableauth',
                        'dolmen.app.authentication',
                        'menhir.contenttype.user',
# Functionalities
                        'dolmen.app.breadcrumbs',
                        'dolmen.app.viewselector',
                        'dolmen.app.search',
                        'menhir.simple.livesearch',
                        'menhir.simple.navtree',
# Content types
                        'menhir.contenttype.document',
                        'menhir.contenttype.file',
                        'menhir.contenttype.folder',
                        'menhir.contenttype.rstdocument',
                        'menhir.contenttype.image',
                        'menhir.contenttype.photoalbum',
# Skins
                        'menhir.skin.lightblue',
#                        'menhir.skin.snappy',"""
        return vars
