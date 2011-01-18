##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="bluebream",
    version='1.0',
    author="Zope Foundation and Contributors",
    author_email="bluebream@zope.org",
    url="http://bluebream.zope.org",
    description="The Zope Web Framework",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        + '\n\n' +
        'Download\n'
        '********'),
    license="ZPL",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Framework :: Zope3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    zip_safe=False,
    include_package_data=True,
    install_requires=["PasteScript>=1.7.3"],
    extras_require={"test": ["zc.buildout"]},
    entry_points={
    "paste.paster_create_template":
        ["bluebream = bluebream.bluebream_base.template:BlueBream",
         ]})

