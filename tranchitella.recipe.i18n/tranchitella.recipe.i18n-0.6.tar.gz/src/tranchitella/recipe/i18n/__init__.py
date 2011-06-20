# tranchitella.recipe.i18n
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>

import logging
import string

from zc.buildout.easy_install import scripts
from zc.recipe.egg.egg import Eggs


class Recipe(object):
    """Buildout recipe: tranchitella.recipe.i18n:default"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.package = options['package']

    def install(self):
        egg = Eggs(self.buildout, self.options["recipe"] + '\n' + self.package,
            self.options)
        requirements, ws = egg.working_set()
        generated = []
        # i18nextract
        arguments = [
            '%sextract'% self.name,
            '-p', self.package,
            '-l', self.options.get('output', 'locales'),
            '-d', self.options.get('domain', self.package),
        ]
        verify_domain = self.options.get('verify_domain')
        if verify_domain is not None:
            arguments.append('--verify-domain')
        exclude = self.options.get('exclude')
        if exclude is not None:
            for e in exclude.split():
                arguments.extend(['--exclude', e])
        zcml = self.options.get('zcml')
        if zcml is not None:
            arguments.extend(['-z', zcml])
        expressions = self.options.get('expressions')
        if expressions is not None:
            for expression in filter(None, map(string.strip,
                expressions.splitlines())):
                arguments.extend(['--expression', expression])
        generated.extend(scripts(
            [(arguments[0], 'tranchitella.recipe.i18n.i18nextract', 'main')],
            ws, self.options['executable'], 'bin', arguments=arguments))
        # i18nstats
        arguments = [
            '%sstats'% self.name,
            '-p', self.package,
            '-l', self.options.get('output', 'locales'),
        ]
        generated.extend(scripts(
            [(arguments[0], 'tranchitella.recipe.i18n.i18nstats', 'main')],
            ws, self.options['executable'], 'bin', arguments=arguments))
        # i18nmerge
        arguments = [
            '%smerge'% self.name,
            '-p', self.package,
            '-l', self.options.get('output', 'locales'),
        ]
        generated.extend(scripts(
            [(arguments[0], 'tranchitella.recipe.i18n.i18nmerge', 'main')],
            ws, self.options['executable'], 'bin', arguments=arguments))
        # i18ncompile
        arguments = [
            '%scompile'% self.name,
            '-p', self.package,
            '-l', self.options.get('output', 'locales'),
        ]
        generated.extend(scripts(
            [(arguments[0], 'tranchitella.recipe.i18n.i18ncompile', 'main')],
            ws, self.options['executable'], 'bin', arguments=arguments))
        return generated

    def update(self):
        self.install()
