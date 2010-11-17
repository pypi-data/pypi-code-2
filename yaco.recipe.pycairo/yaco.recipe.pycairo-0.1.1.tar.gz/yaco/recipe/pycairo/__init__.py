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

import logging
import os
import sys

import pkg_resources

py_version = sys.version[:3]


class PyCairo(object):
    """Recipe for compiling pycairo

    Configuration options:

      - pkg-config-path
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        options.setdefault("site-packages", os.path.join(
            buildout["buildout"]["parts-directory"], name,
            'lib', 'python' + py_version, 'site-packages'))

    def install(self):
        logger = logging.getLogger(self.name)

        cmmi = self.egg = pkg_resources.load_entry_point(
            "zc.recipe.cmmi", "zc.buildout", "default")

        path = [os.path.dirname(sys.executable), os.environ["PATH"]]

        environment = ['PATH=%s' % ':'.join(path)]
        if 'pkg-config-path' in self.options:
            environment.append('PKG_CONFIG_PATH=%s'
                               % self.options['pkg-config-path'])
        options = dict(url=self.options['url'],
                       md5sum=self.options['md5sum'],
                       environment='\n'.join(environment))
        logger.info('Building pycairo')
        dest = cmmi(self.buildout, self.name, options).install()

        return dest

    def update(self):
        pass
