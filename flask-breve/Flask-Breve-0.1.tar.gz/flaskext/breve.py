# -*- coding: utf-8 -*-
"""
    flaskext.breve
    ~~~~~~~~~~~~~~
    
    Usage::
        
        from flaskext.breve import Breve, render_template
        breve = Breve(some_flask_app)
        
    Now::
        
        render_template('admin/index', context={})
    
    renders the file 'index.b' in the admin module's template directory.

    :copyright: (c) 2010 by Daniel Gerber.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import with_statement, absolute_import
import os.path
from werkzeug import cached_property
import flask
import breve
from breve.tags import html as xhtml
try:
    from breve.tags import html4 #broken in current breve
except:
    html4 = xhtml


class TemplateLoader(object):
    """Loads templates from the same places as `~flask.Flask`.
    """
    
    def __init__(self, app):
        self.app = app
        #: paths from flask app
        self.paths = {'': os.path.join(self.app.root_path, 'templates')}
        modules = getattr(self.app, 'modules', {})
        for name, module in modules.iteritems():
            module_path = os.path.join(module.root_path, 'templates')
            if os.path.isdir(module_path):
                self.paths[name] = module_path
    
    def stat(self, template, root):
        template = '%s%s' % (root or '', template)
        module_name, sep, template_name = template.rpartition('/')
        uid = os.path.join(self.paths[module_name], template_name)
##        if not os.path.isfile(uid):
##            raise flask.templating.TemplateNotFound(uid)
        return uid, os.path.getmtime(uid)
    
    def load(self, uid):
        with open(uid, 'rU') as f:
            return f.read()


#: Named configurations for Template instantiation and rendering
methods = {
    'xhtml': {
            'xml_encoding': '<?xml version="1.0" encoding="UTF-8"?>',#XML Decl.
            'doctype': xhtml.doctype, # Doctype Decl.
            'xmlns': xhtml.xmlns, 
            'tags': xhtml.tags}, 
    '(x)html': {
            'xml_encoding': '',
            'doctype': '<!DOCTYPE html>', 
            'xmlns': 'http://www.w3.org/1999/xhtml', 
            'tags': xhtml.tags},
    'html': {
            'xml_encoding': '',#XML Decl.
            'doctype': html4.doctype, # Doctype Decl.
            'xmlns': html4.xmlns, 
            'tags': html4.tags}
    }


class Breve(object):
    
    #: extension for template file names
    #: breve adds a dot in any case
    extension = 'b'
    
    #: XML declaration string
    xml_encoding = ''
    #: Doctype declaration string
    doctype = '<!DOCTYPE html>'
    xmlns = 'http://www.w3.org/1999/xhtml'
    tags = xhtml.tags
    
    namespace = None
    root = None
    
    def __init__(self, app, default_method='(x)html', **options):
        app.breve_instance = self
        self.app = app
        for k, v in methods[default_method].items() + options.items():
            setattr(self, k, v)
        
        # jinja.Environment has decorated versions of these
        try:
            from flaskext.babel import gettext, _, ngettext
            app.context_processor(lambda: {
                    'gettext': gettext, '_': _, 'ngettext': ngettext})
        except:
            pass

    @cached_property
    def template_loader(self):
        return TemplateLoader(self.app)


for k in ['url_for', 'get_flashed_messages']:
    breve.register_global(k, getattr(flask, k))


def render_template(template_name=None, context=None, **options):
    u"""Renders a Brevé template.
    
    :param template_name: as in `flask.render_template` but *without extension*.
    :param context: a dict of context variables
    :param **options: passed on to `breve.Template` or `breve.Template.render`.
    """
    app = flask.current_app
    
    context = context or {}
##    for k in ['config', 'request', 'session', 'g']:
##        context.setdefault(k, getattr(flask, k))
    app.update_template_context(context)
    # keep values injected with app.context_processor
    # not jinja2.contextfunction decorated
##    for k, v in app.jinja_env.globals.iteritems():
##        context.setdefault(k, v)
    
    bi = app.breve_instance
    for k in ['extension', 'xml_encoding', 'doctype', 'xmlns', 'tags', 'root', 'namespace']:
        options.setdefault(k, getattr(bi, k))
    format = options.pop('format', None)
    
    return breve.Template(**options).render(template_name, vars=context, 
                                loader=bi.template_loader, format=format)


def flattened_by(method_name):
    """Class decorator to register the named method as flattener.
    
    Example use::
    
        @flattened_by('__html__')
        class C:
            def __html__(self):
                return '<div>%s</div>' % self
    """
    def decorator(cls):
        breve.register_flattener(cls, getattr(cls, method_name))
        return cls
    return decorator
