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

import os.path
from setuptools import setup, find_packages

name = 'yaco.recipe.uwsgi'
version = '0.2.0'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version=version,
    url='http://trac.yaco.es/cice-buscador',
    author=('Lorenzo Gil'),
    author_email='lgs@yaco.es',
    license='EUPL',
    description='Buildout recipe for compiling uwsgi',
    long_description=(read('README') + '\n\n' + read('CHANGES.txt')),
    keywords='uwsgi buildout',
    classifiers=["Development Status :: 4 - Beta",
                 "Framework :: Buildout"],
    packages=find_packages(),
    namespace_packages=['yaco', 'yaco.recipe'],
    install_requires=['setuptools', 'zc.buildout'],
    entry_points={
        'zc.buildout': ['default = %s:UWSGI' % name],
        },
    zip_safe=False,
    ),
