##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Scrapy buildout based spider development and deployment recipes

"""

import os.path
import zc.buildout
import zc.recipe.egg


def asBool(obj):
    if isinstance(obj, basestring):
        obj = obj.lower()
        if obj in ('1', 'true', 'yes', 't', 'y'):
            return True
        if obj in ('0', 'false', 'no', 'f', 'n'):
            return False
    return bool(obj)



initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])

import scrapy.conf
# fake inproject marker
scrapy.conf.settings.settings_module = True
# settings overrides
"""

env_template = """os.environ['%s'] = %r
"""

overrides_template = """scrapy.conf.settings.overrides['%s'] = %r
"""


class ScrapyRecipeBase:
    """Base class for scrapy script recipes"""

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                                         options.get('script', self.name),
                                         )
        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        if options.get('eggs'):
            self.egg = zc.recipe.egg.Egg(buildout, name, options)

    @property
    def arguments(self):
        # raise error if used and not set in recipe
        return self.options['arguments']

    @property
    def module(self):
        return self.options.get('module', 's01.scrapy.cmdline')

    @property
    def method(self):
        return self.options.get('method', 'execute')

    @property
    def spider(self):
        # raise error if used and not set in recipe
        return self.options['spider']

    @property
    def testing(self):
        return asBool(self.options.get('testing', False))

    def install(self):
        options = self.options
        executable = self.buildout['buildout']['executable']
        settings = options.get('settings', None)
        if settings:
            self.settings = os.path.abspath(settings)
        else:
            self.settings = settings
        self.overrides = options.get('overrides', '')

        # check if we have values
        if not (self.settings or self.overrides):
            raise zc.buildout.UserError("At least one of settings file or " \
                                        "overrides key/values is required")

        # setup additional egg path
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        # first setup optional environment if given
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        # collecct settings
        data = {}
        if settings:
            # load given settings file into dict
            source = open(self.settings, 'rb')
            exec source in data
            # remove __builtins__
            del data['__builtins__']

        # merge additional settings given as overrides key/values into data
        if self.overrides:
            oData = {}
            exec self.overrides in oData
            # remove __builtins__
            del oData['__builtins__']
            # update data with overrides key, values
            data.update(oData)

        # initialize settings data
        initialization = initialization_template
        for key, value in data.items():
            if isinstance(value, (list, dict, basestring)):
                initialization += overrides_template % (key, value)

        # setup testing marker
        if self.testing:
            initialization += overrides_template % ('S01_SCRAPY_TESTING', True)

        # setup script
        return zc.buildout.easy_install.scripts(
            [(options['script'], self.module, self.method)],
            ws, executable, self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = self.arguments,
            initialization = initialization,
            )

        return ()

    update = install


class ScrapyRecipe(ScrapyRecipeBase):
    """Scrapy script recipe"""

    @property
    def arguments(self):
        return self.options.get('arguments', "['scrapy']")


class CrawlRecipe(ScrapyRecipeBase):
    """Scrapy crawl script recipe"""

    @property
    def arguments(self):
        return "['scrapy', 'crawl', '%s']" % self.spider


class ListRecipe(ScrapyRecipeBase):
    """Scrapy list script recipe"""

    @property
    def arguments(self):
        return "['scrapy', 'list']"
