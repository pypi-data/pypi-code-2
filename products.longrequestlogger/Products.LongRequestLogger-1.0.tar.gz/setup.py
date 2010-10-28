##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Leonardo Rochael Almeida <leonardo@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from setuptools import setup
from setuptools import find_packages
import os.path

version = open(os.path.join("Products","LongRequestLogger",
                            "version.txt")).read().strip()
description = "Dumps sequential stack traces of long-running Zope2 requests"

setup(name='Products.LongRequestLogger',
      version=version,
      description=description,
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Intended Audience :: System Administrators",
        ],
      keywords='performance zope2 plone erp5',
      author='Nexedi SA',
      author_email='erp5-dev@erp5.org',
      url='http://www.erp5.com/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      extras_require=dict(
           # With Python versions < 2.5, we need the threadframe module 
           python24=['threadframe'],
           # we need to work with Zope 2.8 buildouts that might not provide a 
           # Zope2 egg (fake or otherwise). So we declare the full dependency
           # here.
           standalone=['Zope2'],
      ),
)
