# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(HERE, 'buildout', 'recipe', 'isolation', 'README.rst')
README = open(README, 'rb')

name = "buildout.recipe.isolation"
setup(
    name=name,
    version="0.1.1",
    author="Michael Mulich | WebLion Group, Penn State University",
    author_email="support@weblion.psu.edu",
    description="Recipe for isolating installed Python package " \
        "distributions and their dependencies",
    long_description=README.read(),
    keywords="development build",
    classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
       ],
    url='http://weblion.psu.edu/trac/weblion/browser/weblion/buildout.recipe.isolation',
    license="GPL 2",
    packages=find_packages(),
    namespace_packages=['buildout', 'buildout.recipe'],
    install_requires=[
        'zc.buildout >=1.0.0b3,<=1.4.3',
        'setuptools', # 'distribute',
        ],
    tests_require=['zope.testing ==3.8.3'],
    # test_suite='__main__.alltests',
    test_suite=name+'.tests.test_suite',
    entry_points={'zc.buildout': ['default=%s:Isolate' % name]},
    include_package_data=True,
    zip_safe=False,
    )
