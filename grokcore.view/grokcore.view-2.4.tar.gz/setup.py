from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

install_requires = [
    'setuptools',
    'grokcore.component >= 2.1',
    'grokcore.security >= 1.5',
    'martian >= 0.13',
    'zope.browserresource >= 3.9.0',
    'zope.component',
    'zope.interface',
    'zope.pagetemplate',
    'zope.ptresource >= 3.9.0',
    'zope.publisher',
    'zope.security',
    'zope.traversing',
    ]

tests_require = [
    'zope.app.wsgi',
    'zope.container',
    'zope.securitypolicy',
    'zope.site',
    'zope.testing',
    'zope.login',
    'zope.configuration',
    'zope.app.appsetup',
    'zope.app.publication',
    'zope.browserpage',
    'zope.password',
    'zope.principalregistry',
    ]

publication_require = [
    'zope.app.publication'
    ]

setup(
    name='grokcore.view',
    version='2.4',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://pypi.python.org/pypi/grok/',
    description='Grok-like configuration for Zope browser pages',
    long_description=long_description,
    license='ZPL',
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 'Framework :: Zope3',
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['grokcore'],
    include_package_data = True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require,
                    'security_publication': publication_require},
)
