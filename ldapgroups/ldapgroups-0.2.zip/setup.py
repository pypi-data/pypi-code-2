from setuptools import setup, find_packages

import os

def read(*rnames):
    return open(os.path.join(*rnames)).read().encode('utf-8')

long_description = (
    read('src', 'ldapgroups', 'README.txt')
    + '\n\n' +
    'Download\n'
    '========\n'
    )

install_requires = ['ldappas>=0.8']

tests_require = install_requires + [
            'zope.testing',
            'zope.testrunner',
            ]



setup(
    name='ldapgroups',
    version='0.2',
    author='Jeroen Michiel',
    author_email='jmichiel@yahoo.com',
    url='http://code.google.com/p/ldapgroups',
    description="""\
A read-only Zope3 GroupFolder implementation that reflects groups on an LDAP server.
Needs ldappas
""",
    long_description=long_description,
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='MIT',
    keywords='Zope3 ldap group folder',
    classifiers = ['Framework :: Zope3',
                   'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP'],
    install_requires=install_requires,
    tests_require = tests_require,
    extras_require=dict(test = tests_require),
    )
