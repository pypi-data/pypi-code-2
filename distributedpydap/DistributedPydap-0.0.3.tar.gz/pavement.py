import string

from paver.easy import *
from paver.setuputils import setup, find_packages, find_package_data
import paver.doctools
import paver.virtual
from paver.release import setup_meta

__version__ = (0,0,3)

options = environment.options
setup(**setup_meta)

options(
    setup=Bunch(
        name='DistributedPydap',
        version='.'.join(str(d) for d in __version__),
        description='Module that implements aggregation of a cluster of Pydap servers.',
        long_description='''
This module brings a WSGI middleware that aggregates datasets from several Pydap servers.

To install it, add the filter to your ``server.ini``::

    [app:main]
    use = egg:pydap#server
    root = %(here)s/data
    templates = %(here)s/templates
    x-wsgiorg.throw_errors = 0
    filter-with = distributed

    [filter:distributed]
    use = egg:DistributedPydap
    root = %(here)s/data
    cache = %(here)s/cache.db

And then add the new ``index.html`` template::

    $ paster create -t DistributedPydap server

Where ``server`` is your installation of Pydap. Then edit the ``index.html`` template
adding the address of other Pydap servers configured with this middleware.
        ''',
        keywords='opendap dods dap data science climate oceanography meteorology',
        classifiers=filter(None, map(string.strip, '''
            Development Status :: 5 - Production/Stable
            Environment :: Console
            Environment :: Web Environment
            Framework :: Paste
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: MIT License
            Operating System :: OS Independent
            Programming Language :: Python
            Topic :: Internet
            Topic :: Internet :: WWW/HTTP :: WSGI
            Topic :: Scientific/Engineering
            Topic :: Software Development :: Libraries :: Python Modules
        '''.split('\n'))),
        author='Roberto De Almeida',
        author_email='rob@pydap.org',
        url='http://pydap.org/',
        license='MIT',

        packages=find_packages(),
        package_data=find_package_data("pydap", package="pydap",
                only_in_packages=False),
        include_package_data=True,
        zip_safe=False,
        namespace_packages=['pydap', 'pydap.wsgi'],

        test_suite='nose.collector',

        dependency_links=[],
        install_requires=[
            'Pydap',
            'WebOb',
            'simplejson',
            'Shove',
            'PasteScript',
        ],
        entry_points="""
            [paste.filter_app_factory]
            main = pydap.wsgi.distributed:make_middleware

            [paste.paster_create_template]
            DistributedPydap = pydap.wsgi.distributed:Template
        """,
    ),
    minilib=Bunch(
        extra_files=['doctools', 'virtual']
    ), 
)


@task
@needs(['generate_setup', 'minilib', 'setuptools.command.sdist'])
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
