"""Low-level versioning support"""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


tests_require = [
    'transaction',
    'zope.annotation',
    'zope.app.component',
    'zope.app.folder',
    'zope.app.testing',
    'zope.testing',
    ]


setup(
    name="zc.vault",
    version="0.11",
    author='Zope Project',
    author_email='zope-dev@zope.org',
    description=__doc__,
    long_description='\n\n'.join([
        read('README.txt'),
        '.. contents::',
        '\n'.join([
            'Detailed Documentation',
            '**********************',
            ]),
        read('src', 'zc', 'vault', 'README.txt'),
        read('CHANGES.txt'),
        ]),
    license='ZPL 2.1',
    keywords="Zope Zope3 version control vault",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    url='http://pypi.python.org/pypi/zc.vault',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'rwproperty',
        'setuptools',
        'zc.copy',
        'zc.freeze',
        'zc.objectlog',
        'zc.relationship',
        'zc.shortcut',
        'ZODB3',
        'zope.app.container',
        'zope.app.intid',
        'zope.app.keyreference',
        'zope.cachedescriptors',
        'zope.component',
        'zope.copypastemove',
        'zope.event',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.location',
        'zope.proxy',
        'zope.publisher',
        'zope.schema',
        'zope.traversing',
        ],
    extras_require=dict(
        test=tests_require,
        ),
    tests_require=tests_require,
    test_suite='zc.vault.tests.test_suite',
    )
