# tranchitella.recipe.i18n
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from setuptools import setup, find_packages

install_requires = [
    'Chameleon',
    'setuptools',
    'zope.component',
    'zc.buildout',
    'zc.recipe.egg',
]

tests_require = []

extras_require = dict(
    test=tests_require,
)

setup(
    name='tranchitella.recipe.i18n',
    version='0.6',
    url='http://pypi.python.org/pypi/tranchitella.recipe.i18n',
    license='GPL 2',
    author='Tranchitella Kft.',
    author_email='info@tranchitella.eu',
    description="Buildout recipe to extract and manage po files",
    long_description=(
        open('README.txt').read() + '\n\n' +
        open('CHANGES.txt').read()
    ),
    classifiers=[
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['tranchitella', 'tranchitella.recipe'],
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=install_requires + tests_require,
    test_suite="tranchitella.recipe.i18n.tests",
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [zc.buildout]
    default = tranchitella.recipe.i18n:Recipe
    """
)
