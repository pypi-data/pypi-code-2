# -*- coding: utf-8 -*-
#
# Sphinx documentation build configuration file

import re
import sphinx

import os
import wuxi

wuxi_theme_dir = os.path.join(os.path.dirname(os.path.abspath(wuxi.__file__)), 'themes')
template_bridge = 'wuxi.bridge.DjangoTemplateBridge'
html_theme_path = [wuxi_theme_dir]
templates_path = ['_templates/wuxi']
#templates_path = ['_templates/orig']
html_theme = 'sphinxdoc'

extensions = [
        'wuxi',
        'sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.todo',
        'sphinx.ext.autosummary', 'sphinx.ext.extlinks']

master_doc = 'contents'
exclude_patterns = ['_build']

project = 'Sphinx'
copyright = '2007-2010, Georg Brandl'
version = sphinx.__released__
release = version
show_authors = True

#html_theme = 'sphinxdoc'
modindex_common_prefix = ['sphinx.']
html_static_path = ['_static']
html_index = 'index.html'
html_sidebars = {'index': ['indexsidebar.html', 'searchbox.html']}
html_additional_pages = {'index': 'index.html'}
html_use_opensearch = 'http://sphinx.pocoo.org'

htmlhelp_basename = 'Sphinxdoc'

epub_theme = 'epub'
epub_basename = 'sphinx'
epub_author = 'Georg Brandl'
epub_publisher = 'http://sphinx.pocoo.org/'
epub_scheme = 'url'
epub_identifier = epub_publisher
epub_pre_files = [('index', 'Welcome')]
epub_exclude_files = ['_static/opensearch.xml', '_static/doctools.js',
    '_static/jquery.js', '_static/searchtools.js',
    '_static/basic.css', 'search.html']

latex_documents = [('contents', 'sphinx.tex', 'Sphinx Documentation',
                    'Georg Brandl', 'manual', 1)]
latex_logo = '_static/sphinx.png'
latex_elements = {
    'fontpkg': '\\usepackage{palatino}',
}

autodoc_member_order = 'groupwise'
todo_include_todos = True
extlinks = {'duref': ('http://docutils.sourceforge.net/docs/ref/rst/'
                      'restructuredtext.html#%s', ''),
            'durole': ('http://docutils.sourceforge.net/docs/ref/rst/'
                       'roles.html#%s', ''),
            'dudir': ('http://docutils.sourceforge.net/docs/ref/rst/'
                      'directives.html#%s', '')}

man_pages = [
    ('contents', 'sphinx-all', 'Sphinx documentation generator system manual',
     'Georg Brandl', 1),
    ('man/sphinx-build', 'sphinx-build', 'Sphinx documentation generator tool',
     '', 1),
    ('man/sphinx-quickstart', 'sphinx-quickstart', 'Sphinx documentation '
     'template generator', '', 1),
]


# -- Extension interface -------------------------------------------------------

from sphinx import addnodes


event_sig_re = re.compile(r'([a-zA-Z-]+)\s*\((.*)\)')

def parse_event(env, sig, signode):
    m = event_sig_re.match(sig)
    if not m:
        signode += addnodes.desc_name(sig, sig)
        return sig
    name, args = m.groups()
    signode += addnodes.desc_name(name, name)
    plist = addnodes.desc_parameterlist()
    for arg in args.split(','):
        arg = arg.strip()
        plist += addnodes.desc_parameter(arg, arg)
    signode += plist
    return name


def setup(app):
    from sphinx.ext.autodoc import cut_lines
    app.connect('autodoc-process-docstring', cut_lines(4, what=['module']))
    app.add_description_unit('confval', 'confval',
                             objname='configuration value',
                             indextemplate='pair: %s; configuration value')
    app.add_description_unit('event', 'event', 'pair: %s; event', parse_event)
