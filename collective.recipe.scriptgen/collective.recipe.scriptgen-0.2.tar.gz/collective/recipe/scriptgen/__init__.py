# -*- coding: utf-8 -*-
"""Recipe z2testrunner"""

from zc.recipe import egg
from zc.buildout import easy_install


class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        python = options.get('python', buildout['buildout']['python'])
        options['executable'] = buildout[python]['executable']
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options.setdefault('eggs', 'zc.recipe.egg')

        self.zcegg = egg.Egg(buildout, options['recipe'], options)

    def install(self):
        """installer"""

        options = self.options
        reqs, ws = self.zcegg.working_set([options['recipe']])

        arguments = [x.strip()
                     for x in options.get('arguments', '').split()
                     if x.strip()]
        env = [x.strip()
               for x in options.get('environment', '').split()
               if x.strip()]
        scr = options['cmd']

        return easy_install.scripts(
            [(self.name, options['recipe'] + '.ctl', 'run')],
            ws,
            options['executable'],
            options['bin-directory'],
            arguments=[scr, arguments, env],
            )

    def update(self):
        """updater"""
        self.install()
