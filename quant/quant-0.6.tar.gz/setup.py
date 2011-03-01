#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, 'src'))

from quant import __version__

basePath = os.path.abspath(os.path.dirname(sys.argv[0]))
scripts = [ 
    os.path.join('bin', 'quant-makeconfig'),
    os.path.join('bin', 'quant-admin'),
    os.path.join('bin', 'quant-test'),
]

setup(
    name='quant',
    version=__version__,

    package_dir={'': 'src'},
    packages=find_packages('src'),
    scripts=scripts,
    # just use auto-include and specify special items in MANIFEST.in
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'domainmodel==0.12',
        'python-dateutil',
        # Installing scipy with setuptools doesn't work.
        #'scipy', 
        #'numpy',
    ],
    author='Appropriate Software Foundation',
    author_email='quant-support@appropriatesoftware.net',
    license='GPL',
    url='http://appropriatesoftware.net/quant',
    description='Enterprise architecture for quantitative analysis in finance.',
    long_description = """

Welcome to Quant
----------------

Quant is an enterprise software application for quantitative analysis.
Quant is a powerful combination of `SciPy <http://www.scipy.org/>`_ and
`DomainModel <http://appropriatesoftware.net/domainmodel/Home.html>`_.

Quant contains a model of quantitative analysis in finance. The model has
object markets, symbols, exchanges, price processes, observations, books,
contract types, pricers, pricer preferences, and reports.

Quant can easily be extended to support custom price processes,
pricers, and contract types. Quant is written in Python.

Quant currently has implementations for a Black Scholes price process; a
Black Scholes pricer, a binomial tree pricer, a monte carlo pricer; and
contract types for european, american and futures contracts.

Some of features we are planning to implement include:

    * scrapers to pull market prices from exchanges;
    * RESTful API for remote machine clients;
    * integration with common spreadsheet applications;
    * domain specific language to specify generic derivatives;
    * monte carlo with state machine to evaluate generic derivatives.

If you would like to suggest a feature, please get in touch!


Install Guide
-------------

It is very easy to install Quant. Creating Quant services involves a few more
steps. Either do it all by hand, or use the Quant installer (see below).

Either way, afterwards you will need to hook Quant into your Apache server.


Operating System Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before installation, make sure required system packages are installed::

    $ sudo aptitude install python python-numpy python-scipy

Check your Python can load scipy with (returns silently if available)::

    $ python -c "import numpy"
    $ python -c "import scipy"

Please note, if you will install Quant into an isolated virtual Python
environment (e.g. with virtualenv), you will want to create library links
to the Python packages for SciPy (and NumPy) before installing Quant.


Install Steps
~~~~~~~~~~~~~

Install the Quant Python package (and dependencies) by running either::

    $ pip install quant

Or by downloading the Quant tarball, unpacking and running::

    $ python setup.py install

After installation, please read the following help pages for more information::

    $ quant-makeconfig --help
    $ quant-admin help setup


Deployment Steps
~~~~~~~~~~~~~~~~

Firstly, decide a filesystem path for the deployment::

    $ mkdir YOUR-SITE-DIR

Secondly, create the configuration file::

    $ quant-makeconfig --master-dir=YOUR-SITE-DIR YOUR-SITE-DIR/quant.conf

Thirdly, set up the site by running::

    $ quant-admin --config=YOUR-SITE-DIR/quant.conf setup

Please note, if you installed Quant into an isolated virtual Python
environment, you will want to use the --virtualenv-bin-dir option of
quant-makeconfig.


The Quant Installer
~~~~~~~~~~~~~~~~~~~

You can create a Quant service in one step with the Quant installer::

    $ wget http://appropriatesoftware.net/provide/docs/quant-virtualenv
    $ chmod +x quant-virtualenv

Run the installer, at least with a path argument (see --help for options)::

    $ ./quant-virtualenv YOUR-SITE-DIR
 
The path argument can be relative or absolute.

The installer will build a virtual Python environment, and install
the Quant software. The installer will then set up a new site with an SQLite
database, and it will create an Apache config file to be included in the main
Apache configuration (see below).


Apache Configuration Steps
~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure the required system packages are installed::

    $ sudo aptitude install apache2 libapache2-mod-wsgi 

Also, make sure Apache mod_wsgi is enabled::

    $ sudo a2enmod wsgi

Change ownership of the Quant files to the Apache server::

    $ sudo chown -R www-data:www-data YOUR-SITE-DIR

You can do more complicated things with the installer (see --help) and
the file permissions and ownerships, but these few lines should work.

Pick a domain name for your site. Create a new virtual host which includes
the auto-generated Apache configuration (path mentioned by the installer).
Then configure your DNS. A new Apache virtual host could simply look like
this::

    <VirtualHost *:80>
        ServerName YOUR-SITE-DOMAIN-NAME
        Include YOUR-SITE-DIR/var/httpd-autogenerated.conf
    </VirtualHost>

Please note, the path to the auto-generated file must be an absolute path (not
a relative path).

After restarting, your virtual host will show a page saying 'Welcome to Quant'.
You will be able to login with username 'admin' and password 'pass'.


Contact
-------

If you have any difficulties or questions about Quant, please email::

    quant-support@appropriatesoftware.net


Please note at the moment, Quant is developed and tested on Ubuntu 10.10 (64 bit)
with Python 2.6 only, although it should work on any recent Linux distribution.


About
-------

Quant is a project of the Appropriate Software Foundation. Please refer to the `Quant website <http://appropriatesoftware.net/quant/Home.html>`_ for more information.

""",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
#        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
#        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)
