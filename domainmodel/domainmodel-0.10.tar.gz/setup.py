from setuptools import setup, find_packages
import sys
sys.path.insert(0, './src')
from dm import __version__

import mx.DateTime  # Because "requires = [egenix-mx-base]" doesn't work.

setup(
    name = 'domainmodel',
    version = __version__,
    package_dir = { '' : 'src' },
    packages = find_packages('src'),
    scripts = ['bin/domainmodel-makeconfig', 'bin/domainmodel-admin', 'bin/domainmodel-test'],
    zip_safe = False,
    include_package_data = True,
    install_requires = [
        'SQLObject>=0.7.10, <=0.12.1',
        'simplejson',
        'markdown>=1.7, <=2.0.5',
        'django>=1.0,<=1.1.1',
        #'egenix-mx-base', # this doesn't work at the moment
    ],
    # Metadata for upload to PyPI.
    author = 'Appropriate Software Foundation, Open Knowledge Foundation',
    author_email = 'kforge-dev@lists.okfn.org',
    license = 'GPL',
    url = 'http://appropriatesoftware.net/domainmodel/Home.html',
    description = 'Toolkit for domain model-based enterprise application frameworks.',
    long_description = \
"""
DomainModel provides a toolkit for domain model-based enterprise application frameworks.

Please refer to the Features page of the domainmodel website for more information.

http://appropriatesoftware.net/domainmodel/Home.html

""",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

