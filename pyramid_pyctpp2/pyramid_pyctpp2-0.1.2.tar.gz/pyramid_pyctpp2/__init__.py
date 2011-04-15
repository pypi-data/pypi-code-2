# Copyright (c) 2011 Volvox Development Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

import threading
import os
from stat import ST_MTIME
import hashlib

import pyctpp2

from pyramid.asset import abspath_from_asset_spec
from pyramid.interfaces import ITemplateRenderer
from pyramid.i18n import get_locale_name
from zope.interface import implements
from zope.interface import Attribute
from zope.interface import Interface

class IPyCTPP2Engine(Interface):
    pass

class ITemplate(Interface):
    instance = Attribute("""pyctpp2 Template object""")
    mtime = Attribute("""Last modified time""")

class PyCTPP2Template(object):
    implements(ITemplate)

    def __init__(self, instance, mtime):
        self.instance = instance
        self.mtime = mtime


registry_lock = threading.Lock()

def renderer_factory(info):
    engine = pyctpp2.Engine()
    with registry_lock:
        info.registry.registerUtility(engine, IPyCTPP2Engine)
    return PyCTPP2TemplateRenderer(info, engine)


class ITemplateSettings(Interface):
    locales = Attribute("""Locales dictionary""")
    path = Attribute("""Template path""")

    def add_translation(domain, path):
        """Add i18n translation. Bind text domain to locale directory."""

    def add_template_path(path):
        """Add path to CTPP2 templates."""


class PyCTPP2Settings():
    implements(ITemplateSettings)

    def __init__(self):
        self.locales = {}
        self.path = []

    def add_translation(self, domain, path):
        self.locales[domain] = path

    def add_template_path(self, path):
        self.path.append(path)


class PyCTPP2TemplateRenderer(object):
    '''Renderer for a pyctpp2 template'''
    implements(ITemplateRenderer)

    template = None

    def __init__(self, info, engine):
        self.info = info
        self.engine = engine
        self.path = info.settings.get('pyctpp2.template.path', '')
        self.path = [abspath_from_asset_spec(p) for p in self.path.split()]
        self.engine.path = self.path

        registry = self.info.registry
        self.tmpl_settings = registry.queryUtility(ITemplateSettings)
        if self.tmpl_settings is None:
            self.tmpl_settings = PyCTPP2Settings()
            registry.register(self.tmpl_settings)

        domain = info.settings.get('pyctpp2.i18n.domain', '')
        if domain:
            self.engine.set_default_domain(domain)

            folder = info.settings.get('pyctpp2.i18n.path', '')
            if folder:
                folder = abspath_from_asset_spec(folder)
                self.engine.add_translation(domain, folder)


    def implementation(self):
        return self.template

    def _parse_with_saving(self, path):
        m = hashlib.md5()
        m.update(path)
        ct_key = m.hexdigest()

        last_modified = os.stat(path)[ST_MTIME]
        template = self.info.registry.queryUtility(ITemplate, ct_key)
        if template is None or template.mtime < os.stat(path)[ST_MTIME]:
            instance = self.engine.parse(path)
            template = PyCTPP2Template(instance, last_modified)
            self.info.registry.registerUtility(template, ITemplate, ct_key)

        return template.instance

    @property
    def template(self):
        if len(self.tmpl_settings.path):
            tmpl_path = [abspath_from_asset_spec(p) for p in self.tmpl_settings.path]
            self.engine.path = self.engine.path + tmpl_path
            self.tmpl_settings.path = []

        isabs = os.path.isabs(self.info.name)

        filename = self.info.name
        if (not isabs) and (':' in filename):
            pname, spec = filename.split(':')
            filename = abspath_from_asset_spec(filename, spec)

        (name, ext) = os.path.splitext(filename)

        if not isabs:
            for p in self.path:
                likely_path = os.path.join(p, filename)
                if os.path.exists(likely_path):
                    return self._parse_with_saving(likely_path)
        elif self.cache_dir:
            return self._parse_with_saving(filename)

        return self.engine.parse(filename)

    def __call__(self, value, system):
        if len(self.tmpl_settings.locales):
            for domain, folder in self.tmpl_settings.locales.items():
                folder = abspath_from_asset_spec(folder)
                self.engine.add_translation(domain, folder)
            self.tmpl_settings.locales = {}

        loc = None
        if 'request' in system:
            loc = get_locale_name(system['request'])
        return self.template.render(value, locale=loc)

def includeme(config):
    '''Setup standard configurator registrations.'''
    config.add_renderer('.tmpl', renderer_factory)

