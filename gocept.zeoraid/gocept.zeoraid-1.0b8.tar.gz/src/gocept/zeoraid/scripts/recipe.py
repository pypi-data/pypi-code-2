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
"""Recipe to create a ZEO server with additional RAID management scripts.

The recipe is compatible to (and uses internally) zc.zodbrecipes:server.

"""


import ZConfig.schemaless
import cStringIO
import os.path
import zc.zodbrecipes


class ZEORAIDServer(object):

    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options
        self.buildout = buildout

        options['eggs'] = options.get('eggs', '')
        options['eggs'] += '\ngocept.zeoraid'

        # Other recipes we facilitate
        self.egg = zc.recipe.egg.Egg(buildout, name, options)
        self.zeo = zc.zodbrecipes.StorageServer(buildout, name, options)

    def install(self):
        paths = self.zeo.install()
        paths.extend(self.egg.install())

        if self.zeo.deployment:
            # Mimick zc.zodbrecipes here
            rc = self.options['deployment-name'] + '-' + self.name
        else:
            rc = self.name

        # Analyse zeo.conf template for storages and the host/port
        zeo_conf = self.options.get('zeo.conf', '')+'\n'
        zeo_conf = ZConfig.schemaless.loadConfigFile(
            cStringIO.StringIO(zeo_conf))

        # Determine host/port
        zeo_section = [s for s in zeo_conf.sections if s.type == 'zeo']
        if not zeo_section:
            raise zc.buildout.UserError('No zeo section was defined.')
        if len(zeo_section) > 1:
            raise zc.buildout.UserError('Too many zeo sections.')
        zeo_section = zeo_section[0]
        if not 'address' in zeo_section:
            raise zc.buildout.UserError('No ZEO address was specified.')
        address = zeo_section['address'][0].split(':')
        if len(address) == 2:
            host, port = address
        elif len(address) == 1:
            host, port = '127.0.0.1', int(address[0])
        else:
            raise zc.buildout.UserError(
                'Invalid ZEO address %r was specified.' %
                zeo_section['address'][0])

        # Determine the RAID storages
        storages = [s.name for s in zeo_conf.sections
                    if s.type == 'raidstorage'
                    ]

        # Create RAID control scripts for all RAID storages
        requirements, working_set = self.egg.working_set()
        for storage in storages:
            script_name = '%s-%s-manage' % (rc, storage)
            paths.append(os.path.join(self.options['rc-directory'],
                                      script_name))
            zc.buildout.easy_install.scripts(
                requirements, working_set,
                self.options['executable'],
                self.options['rc-directory'],
                scripts={'zeoraid': script_name},
                arguments='port=%s, host="%s", storage="%s"' % (
                    port, host, storage))
        return paths

    update = install
