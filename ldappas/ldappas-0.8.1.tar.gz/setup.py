from setuptools import setup, find_packages

tests_require = [
    'zope.app.testing',
    ]

setup(
    name='ldappas',
    version='0.8.1',
    author='Zope developers',
    author_email='zope-dev@zope.org',
    url='http://svn.zope.org/ldappas',
    description="""\
LDAP-based authenticator for Zope 3. It uses ldapadapter to talk to an
LDAP server.
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL 2.1',
    keywords='Zope3 authentication ldap',
    install_requires=[
        'ZODB3',
        'ldapadapter>0.6',
        'setuptools',
        'zope.pluggableauth',
        'zope.container',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        'zope.app.testing',
    ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
    )
