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

import logging
import os
import os.path
import sys
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


class LoggerMixin(object):
    """Logging support."""

    _loggerName = None
    _logger = None

    @apply
    def loggerName():
        def fget(self):
            return self._loggerName
        def fset(self, loggerName):
            self._loggerName = loggerName
            self._logger = logging.getLogger(self._loggerName)
        return property(fget, fset)

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(self.loggerName)
        return self._logger


class CHMODMixin(LoggerMixin):
    """chmode support."""

    def doChmod(self, filename, mode):
        if not filename or not mode:
            return
        os.chmod(filename, self.mode)
        msg = "Change mode %s for %s" % (mode, filename)
        self.logger.info(msg)



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


class ScrapyRecipeBase(LoggerMixin):
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

        # by default log to the s01.worker logger
        self.loggerName = options.get('logger', 's01.worker')

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
    def testing(self):
        return asBool(self.options.get('testing', False))

    def validate(self):
        # by default it's allowed to use without settings
        pass

    def install(self):
        options = self.options
        executable = self.buildout['buildout']['executable']
        self.settings = options.get('settings', None)
        self.overrides = options.get('overrides', '')

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

        # collect settings, settings could be a section with a target or
        # a file path. You can use the p01.scrapy:settings recipe for create
        # a file with such a section target or just point to an existing file
        # path
        data = {}
        if self.settings:
            section = self.buildout.get(self.settings)
            if section:
                # it's a section and not a file, load it from target
                sPath = section['target']
                self.logger.info('Load settings given from section target %s'  %
                    sPath)
            else:
                sPath = os.path.abspath(self.settings)
                self.logger.info('Load settings from path %s' % sPath)
            if not os.path.exists(sPath):
                msg = 'Missing settings path %s' % sPath
                self.logger.info(msg)
                raise zc.buildout.UserError(msg)
            # load given settings file into dict
            source = open(sPath, 'rb')
            exec source in data
            # remove __builtins__
            del data['__builtins__']

        # merge additional settings given as overrides key/values into data
        if self.overrides:
            self.logger.info('Load overrides')
            oData = {}
            exec self.overrides in oData
            # remove __builtins__
            del oData['__builtins__']
            # update data with overrides key, values
            data.update(oData)

        # initialize settings data
        initialization = initialization_template
        for key, value in data.items():
            if isinstance(value, basestring):
                if '\t' in value or '\n' in value:
                    # fix bad sting parts
                    value = value.replace('\t', '\\t')
                    value = value.replace('\n', '\\n')
                    value = value.replace('\\\r', '\\r')
                    value = value.replace('\\\n', '\\n')
                initialization += overrides_template % (key, value)
            elif isinstance(value, (dict, list)):
                initialization += overrides_template % (key, value)

        # setup testing marker
        if self.testing:
            self.logger.info('Enable testing option')
            initialization += overrides_template % ('S01_SCRAPY_TESTING', True)

        # setup script
        return zc.buildout.easy_install.scripts(
            [(options['script'], self.module, self.method)],
            ws, executable, self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = self.arguments,
            initialization = initialization,
            )

    update = install


# scripts without settings
class ScrapyRecipe(ScrapyRecipeBase):
    """Scrapy script recipe"""

    @property
    def arguments(self):
        return self.options.get('arguments', "['scrapy']")


# scripts with required soider settings
class SettingsRequiredMixin(object):
    """Check missing settings"""

    def validate(self):
        # check if we have settings
        if not (self.settings or self.overrides):
            raise zc.buildout.UserError("At least one of settings file or " \
                                        "overrides key/values is required")


class CrawlRecipe(SettingsRequiredMixin, ScrapyRecipeBase):
    """Scrapy crawl script recipe"""

    @property
    def arguments(self):
        return "['scrapy', 'crawl']"


class ListRecipe(SettingsRequiredMixin, ScrapyRecipeBase):
    """Scrapy list script recipe"""

    @property
    def arguments(self):
        return "['scrapy', 'list']"


class SettingsRecipe(CHMODMixin):
    """Create settings file based on file path using file(path, 'w')
    because of path convertion.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name
        self.mode = int(options.get('mode', '0644'), 8)
        # touch content, raises error if missing
        options['content']
        self.originalPath = options['target']
        options['target'] = os.path.join(buildout['buildout']['directory'],
            self.originalPath)
        self.createPath = options.get('createpath', 'False').lower() in [
            'true', 'on', '1']

        # by default log to the s01.worker logger
        self.loggerName = options.get('logger', 's01.worker')

    def install(self):
        target = self.options['target']
        dirname = os.path.dirname(target)
        if not os.path.isdir(dirname):
            self.logger.info('Creating directory %s', dirname)
            os.makedirs(dirname)
        f = file(target, 'w')
        self.logger.info('Writing file %s', target)
        content = self.options['content']
        if sys.platform == 'win32':
            # quick windows path cleanup hack, hope this will not messup
            content = content.replace('\\', '/')
        f.write(content)
        f.close()
        self.doChmod(target, self.mode)
        return target
