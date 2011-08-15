"""
setup.py

AIGO is a python library for
the Analysis and Inter-comparison of Gene Ontology functional annotations.
see (http://code.google.com/p/aigo).
        
Created by Michael Defoin-Platel on 21/02/2010.
Copyright (c) 2010. All rights reserved.

AIGO is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from distutils.core import setup

setup(
    name='AIGO',
    version='0.1.0',
    author='Michael Defoin-Platel',
    author_email='michael.defoinplatel@gmail.com',
    packages=['AIGO', 'AIGO.go', 'AIGO.utils', 'AIGO.gui', 'tests'],
    package_dir={'AIGO.gui': 'AIGO/gui'},
    package_data={'AIGO.gui': ['*.png']},    
    scripts=['bin/AIGO-gui.py'],
    url='http://pypi.python.org/pypi/AIGO/',
    license='LICENSE.txt',
    description='Analysis and Inter-comparison of Gene Ontology functional annotations',
    long_description=open('README.txt').read(),
)
