##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Paste deploy recipes for Zope3 apps

$Id:$
"""

import os
import cStringIO
import ZConfig.schemaless
import zc.buildout
import zc.recipe.egg


class PasteServeSetup:
    """Paste serve setup script without checking zodb part in conf section"""

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

        if options.get('eggs') is None:
            raise zc.buildout.UserError(
                'You have to define at least one egg for setup an application.')
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        options = self.options
        location = options['location']
        executable = self.buildout['buildout']['executable']

        # setup path
        dest = []
        if not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)

        event_log_path = os.path.join(location, 'error.log')
        site_zcml_path = os.path.join(location, 'paste.zcml')

        # append file to dest which will remove it on update
        dest.append(site_zcml_path)


        # setup site zcml
        open(site_zcml_path, 'w').write(
            site_zcml_template % self.options['zcml']
            )

        # setup *.ini file
        ini_conf = options.get('ini', '')+'\n'
        ini_path = os.path.join(location, 'paste.ini')
        open(ini_path, 'w').write(str(ini_conf))

        # append file to dest which will remove it on update
        dest.append(ini_path)

        # setup zope conf
        conf = options.get('conf', '')+'\n'
        conf = ZConfig.schemaless.loadConfigFile(
            cStringIO.StringIO(conf))

        conf['site-definition'] = [site_zcml_path]

        if not [s for s in conf.sections if s.type == 'eventlog']:
            conf.sections.append(event_log(event_log_path))

        conf_path = os.path.join(location, 'paste.conf')
        open(conf_path, 'w').write(str(conf))

        # append file to dest which will remove it on update
        dest.append(conf_path)

        # setup paster script
        if self.egg is not None:
            extra_paths = self.egg.extra_paths
        else:
            extra_paths = []

        eggs, ws = self.egg.working_set()

        defaults = options.get('defaults', '').strip()
        if defaults:
            defaults = '(%s) + ' % defaults

        initialization = initialization_template
        dest.extend(zc.buildout.easy_install.scripts(
            [('%s'% self.name, 'paste.script.command', 'run')],
            ws, self.options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = defaults + (arg_template % dict(
                INI_PATH=ini_path,
                )),
            initialization = initialization_template
            ))

        return dest

    update = install


# setup helper
arg_template = """[
  'serve', %(INI_PATH)r,
  ]+sys.argv[1:]"""


site_zcml_template = """\
<configure
    xmlns="http://namespaces.zope.org/zope">
%s

</configure>
"""


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""

def event_log(path, *data):
    return ZConfig.schemaless.Section(
        'eventlog', '', None,
        [ZConfig.schemaless.Section(
             'logfile',
             '',
             dict(path=[path])),
         ])
