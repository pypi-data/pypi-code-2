#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#  This file is part of django-recaptcha-works.
#
#  django-recaptcha-works provides a Django form field that integrates the
#  reCaptcha service.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-recaptcha-works
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-recaptcha-works
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
#
#  Based on the code snippet #1644 as published on:
#    - http://djangosnippets.org/snippets/1644/
#
#  Copyright (c) 2009-2010 Chris Beaven, http://smileychris.com/
#
#  Licensed under the BSD License.
#
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#
#      1. Redistributions of source code must retain the above copyright notice, 
#         this list of conditions and the following disclaimer.
#      
#      2. Redistributions in binary form must reproduce the above copyright 
#         notice, this list of conditions and the following disclaimer in the
#         documentation and/or other materials provided with the distribution.
#
#      3. Neither the name of Django nor the names of its contributors may be used
#         to endorse or promote products derived from this software without
#         specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#  ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#  NOTES
#
#  Create source distribution tarball:
#    python setup.py sdist --formats=gztar
#
#  Create binary distribution rpm:
#    python setup.py bdist --formats=rpm
#
#  Create binary distribution rpm with being able to change an option:
#    python setup.py bdist_rpm --release 7
#
#  Test installation:
#    python setup.py install --prefix=/usr --root=/tmp
#
#  Install:
#    python setup.py install
#  Or:
#    python setup.py install --prefix=/usr
#

import sys
import os
sys.path.insert(0, os.path.abspath('src'))

from setuptools import setup

from recaptcha_works import get_version, long_description

if __name__=='__main__':
    setup(
        name = 'django-recaptcha-works',
        version = get_version(),
        license = 'BSD License',
        author = 'George Notaras',
        author_email = 'gnot [at] g-loaded.eu',
        maintainer = 'George Notaras',
        maintainer_email = 'gnot [at] g-loaded.eu',
        url = 'http://www.codetrax.org/projects/django-recaptcha-works',
        description = 'django-recaptcha-works provides a Django form field that integrates the reCaptcha service.',
        long_description = long_description,
        download_url = 'https://source.codetrax.org/hgroot/django-recaptcha-works',
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        package_dir = {'': 'src'},
        packages = ['recaptcha_works'],
        include_package_data = True,
        #zip_safe = False,
    )

