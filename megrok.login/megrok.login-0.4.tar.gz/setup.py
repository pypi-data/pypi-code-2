from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

tests_require = [
    'zope.testing',
    'zope.app.testing',
    'zope.testbrowser',
    'z3c.testsetup',
    ]

long_description = (
    read('README.txt')
    + '\n\n'
    + 'Detailed Documentation\n'
    + '**********************\n'
    + '\n'
    + read('src', 'megrok', 'login', 'README.txt')
    + '\n\n'
    + read('CHANGES.txt')
    + '\n\n'
    + 'Download\n'
    + '********\n'
    )

setup(
    name='megrok.login',
    version='0.4',
    author='Uli Fouquet and the Zope Community',
    author_email='uli@gnufix.de',
    url = 'http://pypi.python.org/pypi/megrok.login',
    description='Providing login screens for your Grok apps made easy.',
    long_description=long_description,
    license='ZPL 2.1',
    keywords="zope3 zope login grok security PAU",
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 'Framework :: Zope3',
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['megrok'],
    include_package_data = True,
    zip_safe=False,
    install_requires=['setuptools',
                      'grok',
                      'martian',
                      'zope.authentication',
                      'zope.container',
                      'zope.component',
                      'zope.interface',
                      'zope.pluggableauth',
                      'zope.securitypolicy',
                      ],
    tests_require = tests_require,
    extras_require = dict(test=tests_require),
)
