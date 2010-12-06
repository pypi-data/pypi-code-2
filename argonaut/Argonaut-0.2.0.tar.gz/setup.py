try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='Argonaut',
    version='0.2.0',
    description='Lightweight Pylons powered blogging engine.',
    author='Jason Robinson',
    author_email='jaywink@basshero.org',
    url='http://www.basshero.org',
    download_url='http://pypi.python.org/pypi/Argonaut',
    install_requires=[
        "Pylons>=1.0",
        "SQLAlchemy>=0.5",
        "repoze.what-pylons",
        "repoze.what-quickstart",
        "hashlib",
        "TurboMail"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'argonaut': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'argonaut': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = argonaut.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Environment :: Web Environment",
        "Framework :: Pylons",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI"
    ],
    keywords='python pylons blogging cms blog',
    license='FreeBSD',
    long_description='''
ARGONAUT   
========

Version 0.2.0 (6th December 2010)

Author: Jason Robinson
jaywink@basshero.org
http://www.basshero.org


1. Description
==============

Argonaut is a blogging engine built with Pylons. It is lightweight
and can be deployed on many types of web servers running Python.

This release is the first public release of Argonaut. The application is
still very much in alpha stages and as such there are bugs in the
system and a lot of features which have not been implemented.

For more information please see the following links:
    Authors webpage
       http://www.basshero.org
    Pylons HQ
       http://www.pylonshq.com


2. Licence
==========

Argonaut is distributed under the FreeBSD license. This means you can use,
copy and distribute the code and application for free and with no obligations.
It is however required that the included copyright is included with the application
using source or binary components. Please see the file LICENSE.txt for the full
license.

The licenses of the JavaScript components included with Argonaut do not
enforce any additional requirements for reuse or distribution. Please see the
licenses of these components in the folder 'third_party_licenses'.


3. Installation
===============

3.1 Prequisites for install
---------------------------

- Python 2.4+ [http://www.python.org]
- Pylons 1.0 [http://pylonshq.com/]
- Python setuptools (easy_install) [http://pypi.python.org/pypi/setuptools]

Please see Pylons documentation to get started with Pylons [http://pylonshq.com/docs/en/0.9.7/gettingstarted/].


3.2 Other components
--------------------

In addition to Pylons, Argonaut uses the following components:

- Mako (templates, the View) [http://www.makotemplates.org/]
- SQLAlchemy (the Model) [http://www.sqlalchemy.org/]
- repoze.what (authentication and access rights) [http://what.repoze.org/docs/1.0/]
- CKEditor (for writing posts) [http://ckeditor.com/]
- AddToAny (for sharing) [http://www.addtoany.com/]
- jQuery (for additional magic) [http://jquery.com/]
- Simple3color (default theme) [http://www.oswd.org/design/preview/id/3533]
- TurboMail (for notifications) [http://www.python-turbomail.org/]

Of these the JavaScript components CKEditor, jQuery and AddToAny are
distributed along with this package. The Python components are downloaded
and installed by easy_install.


3.3 Installation and Setup
--------------------------

Prequisites for install must be fulfilled. Install Argonaut using easy_install:

    easy_install argonaut
    
       OR with local .egg file
       
    easy_install <path_to_egg_file>

Make a config file as follows:

    paster make-config argonaut config.ini

Tweak the config file as appropriate. Please see Pylons application
setup pages for hints on editing the config file [http://pythonpaste.org/deploy/].
After this run the following to setup the application:

    paster setup-app config.ini#arg

Then you are ready to go.

You can test the installation by running:

    paster serve config.ini

After this visit the link http://127.0.0.1:5000

Optionally no installing is needed to just test the application. 
Just extract the source, install Pylons and in the Argonaut
base directory run:
    
    paster serve development.ini


4. Usage
========

4.1 Modifying the site
----------------------

Argonaut features templates that can be used to control the site
structure, layout and texts. Unfortunately in this early version
there is no admin panel so all editing must be made to the files
directly.

Template files are situated in argonaut/templates. Please see
Mako documentation on how to change the templates.


4.2 Configuration
-----------------

During application setup a database will be created in the form
that is configured in config.ini. In addition to blog data, Argonaut
also stores some configuration values in the database. These are 
stored in the table 'config'.


4.3 Users
---------

The default user for writing posts is 'admin', password 'admin'.
Currently users can only be added directly to the database. An
admin panel will be added later.


4.4 Other usage notes
---------------------

Proper documentation and usage will be added slowly over
future releases :)


5. Support
==========

Please contact the author at jaywink@basshero.org for support,
ideas and bug reports.

'''
)
