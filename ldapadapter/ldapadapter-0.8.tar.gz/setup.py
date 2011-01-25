from setuptools import setup, find_packages

setup(
    name='ldapadapter',
    version='0.8',
    author='Zope developers',
    author_email='zope-dev@zope.org',
    url='http://svn.zope.org/ldapadapter',
    description="""\
LDAP connection for Zope Toolkit. Connects to an LDAP server.
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL 2.1',
    keywords='Zope3 ZTK authentication ldap',
    install_requires=[
        'setuptools',
        'python-ldap',
        'ZODB3',
        'zope.interface',
        'zope.component',
        'zope.schema',
        'zope.container',
        'zope.componentvocabulary',
        'zope.security',
        'zope.i18nmessageid',
    ],
    extras_require=dict(
        test=[
            'zope.testing',
        ])
    )

