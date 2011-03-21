# Copyright (c) 2011 by Yaco Sistemas  <lgs@yaco.es>
#
# This file is part of yaco.recipe.cert
#
# yaco.recipe.cert is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# yaco.recipe.cert is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with yaco.recipe.cert.
# If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import subprocess

import zc.buildout


class CertificateGenerator(object):

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        self.hostname = options.get('hostname', 'example.com')
        self.country = options.get('country', 'ES')
        self.city = options.get('city', 'Sevilla')
        self.organization = options.get('organization', 'Yaco Sistemas S.L.')
        self.locality = options.get('locality', 'Sevilla')

        self.basedir = buildout['buildout']['parts-directory']

    def install(self):
        logger = logging.getLogger(self.name)
        basefile = os.path.join(self.basedir, self.hostname)

        # Generate a rsa key
        key_filename = basefile + '.key'
        logger.info('Creating private key in "%s"' % key_filename)
        cmd = 'openssl genrsa -out %s 2048' % key_filename
        retcode = subprocess.call(cmd.split(' '))
        if retcode != 0:
            logger.error('Error while generating private key in "%s"'
                         % key_filename)
            raise zc.buildout.UserError('Error while generating private key')

        # Generate the certificate request
        csr_filename = basefile + '.csr'
        logger.info('Creating certificate request in "%s"' % csr_filename)
        subj = '/C=%s/ST=%s/O=%s/localityName=%s/commonName=%s/' % (
            self.country, self.city, self.organization,
            self.locality, self.hostname)
        cmd = ['openssl', 'req', '-new', '-batch', '-nodes', '-subj', subj,
               '-key', key_filename, '-out', csr_filename]
        retcode = subprocess.call(cmd)
        if retcode != 0:
            logger.error('Error while generating certificate request in "%s"'
                         % csr_filename)
            raise zc.buildout.UserError('Error while generating '
                                        'certificate request')

        # Create the certificate file
        crt_filename = basefile + '.crt'
        logger.info('Creating certificate file in "%s"' % crt_filename)
        cmd = ('openssl x509 -req -days 365 -in %s -signkey %s -out %s'
               % (csr_filename, key_filename, crt_filename))
        retcode = subprocess.call(cmd.split(' '))
        if retcode != 0:
            logger.error('Error while generating the certificate file in "%s"'
                         % crt_filename)
            raise zc.buildout.UserError('Error while generating certificate file')

        return (key_filename, csr_filename, crt_filename)

    def update(self):
        pass
