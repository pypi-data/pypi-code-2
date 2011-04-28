# Copyright 2010 Junta de Andalucia
#
# Developed by Yaco Sistemas <lgs@yaco.es>
#
# Licensed under the EUPL, Version 1.1 or - as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.

import os
import shutil
import sys

UWSGI_CONFIG_MODULE = 'uwsgiconfig'


class UWSGI(object):
    """Recipe for compiling uWSGI

    Configuration options:

      - uwsgi-location
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.uwsgi_location = self.options['uwsgi-location']

    def install(self):
        old_dir = os.getcwd()
        os.chdir(self.uwsgi_location)
        old_files = os.listdir(self.uwsgi_location)

        if self.uwsgi_location not in sys.path:
            sys.path.append(self.uwsgi_location)
            sys_path_changed = True

        uwsgiconfig = __import__(UWSGI_CONFIG_MODULE)
        conf = uwsgiconfig.uConf('buildconf/default.ini')
        conf.cflags.remove('-Werror')
        uwsgiconfig.build_uwsgi(conf)

        os.chdir(old_dir)
        if sys_path_changed:
            sys.path.remove(self.uwsgi_location)

        new_files = os.listdir(self.uwsgi_location)

        bin = os.path.join(self.buildout['buildout']['bin-directory'])
        shutil.copy(os.path.join(self.uwsgi_location, 'uwsgi'), bin)
        files = list(set(new_files) - set(old_files))
        files.append(os.path.join(bin, 'uwsgi'))
        return files

    def update(self):
        pass
