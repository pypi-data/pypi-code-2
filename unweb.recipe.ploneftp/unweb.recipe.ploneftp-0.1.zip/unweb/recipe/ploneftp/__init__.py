# -*- coding: utf-8 -*-
"""Recipe ploneftp"""
import os, re, shutil
import zc.buildout
import zc.recipe.egg

from os.path import abspath, dirname, join, exists
from unweb.recipe.ploneftp.config import tmp_dir as default_tmp_dir
from unweb.recipe.ploneftp.config import zope_ftp_address as default_zope_ftp_address
from unweb.recipe.ploneftp.config import address as default_address
from unweb.recipe.ploneftp.config import login_message as default_login_message
from unweb.recipe.ploneftp.config import logout_message as default_logout_message
from unweb.recipe.ploneftp.config import path as default_path
from unweb.recipe.ploneftp import zope_ftpd

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )
        options['bin-directory'] = buildout['buildout']['bin-directory']

    def install(self):
        """Installer"""
        options = self.options
        location = options['location']

        bodir = self.buildout['buildout']['directory']

        self.preparePartDir()

        extra_paths = options.get('extra-paths', '').split()
        extra_paths.append(bodir)

        requirements, ws = self.egg.working_set(['unweb.recipe.ploneftp'])

        #Generating the script
        zc.buildout.easy_install.scripts(
            [(self.options.get('control-script', self.name),
                'unweb.recipe.ploneftp.ctl', 'main')],
            ws, options['executable'], options['bin-directory'],
            extra_paths = extra_paths,
            #Passing arguments to the ctl main function
            arguments = ('\n        [%r]'
                         '\n        + sys.argv[1:]'
                         % location
                         ),
            #So we can use paths relative to the buildout directory!!
            initialization='import os\nos.chdir("%s")' % bodir,
            )

        return tuple()


    def preparePartDir(self):
        location = self.options['location']

        conf = join(location, 'config.py')

        if not exists(location):
            os.mkdir(location)
        self.writeConf(conf)


    def writeConf(self, filename):
        tmp_dir = self.options.get('tmp_dir', default_tmp_dir)
        zope_ftp_address = self.options.get('zope_ftp_address', default_zope_ftp_address)
        address = self.options.get('address', default_address)
        login_message = self.options.get('login_message', default_login_message)
        logout_message = self.options.get('logout_message', default_logout_message)
        path = self.options.get('path', default_path)

        conf_file = file(filename, 'w')
        conf_file.write('tmp_dir = "%s"'% tmp_dir + '\n')
        conf_file.write('zope_ftp_address = "%s"'% zope_ftp_address + '\n')
        conf_file.write('address = "%s"'% address + '\n')
        conf_file.write('login_message = "%s"'% login_message + '\n')
        conf_file.write('logout_message = "%s"'% logout_message + '\n')
        conf_file.write('path = "%s"'% path + '\n')
        conf_file.close()


    def update(self):
        """Updater"""
        self.install()
