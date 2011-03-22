from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

version = '0.4.4'

setup(
    name= 'Shabti',
    version=version,
    author="Graham Higgins",
    author_email="gjh@bel-epa.com",
    keywords='web wsgi framework sqlalchemy elixir pylons paste template',
    description='Pylons template with Elixir ORM bindings',
    long_description="""
Shabti
======

Shabti is a set of Pylons kick-start services built on Pylons/Paste and, variously Elixir, SQLAlchemy, rdflib, RDFAlchemy. It includes paster commands for database management, migrations and model scaffolding, plus AuthKit integration. With just a little bit of glue Shabti gives you a major kick-start using the best Python web development libraries around today.

Current Status
---------------

Shabti %s described on this page is stable.

There is also an unstable `development version
<http://www.bitbucket.org/gjhiggins/shabti/get/tip.tar.gz#egg=Shabti-dev>`_ of Shabti.

Download and Installation
-------------------------

Shabti can be installed with `Easy Install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_ by typing::

 > easy_install Shabti


More information
----------------

Check out the project home pages on `BitBucket <http://www.bitbucket.org/gjhiggins/shabti/overview/>`_
and `Bel-EPA <http://bel-epa.com/shabtidocs/>`_

""" % version,
    license='MIT License',
    url='http://www.bitbucket.org/gjhiggins/shabti',
    dependency_links=[
        "http://www.bitbucket.org/gjhiggins/shabti/overview/"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pylons",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
    packages=find_packages(),
    install_requires=["Pylons==1.0", 
                      "Elixir>=0.6",
                      "SQLAlchemy>=0.5.8"],
    extras_require={"migrate" : ["sqlalchemy-migrate>=0.5.3"],
                    "rdfal" : ["RDFAlchemy>=0.2b1"],
                    "rdflib" : ["rdflib>=2.4.0,<=3.0"],
                    "couchdb" : ["CouchDB>=0.4", "httplib2>=0.4.0"],
                    "authplus" : ["FormAlchemy", "fa.jquery>=0.6",
                                  "python-openid>=2.2.1", "Babel>=0.9.4", 
                                  "pytz>=2008i", "tw.forms>=0.9.3",
                                  "docutils>=0.5", "cssutils>=0.9.6a0", 
                                  "Pygments>=1.0"],
                    "couchdbkit" : ["FormAlchemy", "fa.jquery>=0.6", "couchdbkit"],
                    "formalchemy" : ["FormAlchemy", "fa.jquery>=0.6"],
                    "humanoid" : ["FormAlchemy", "fa.jquery>=0.6", "py-bcrypt>=0.1"],
                    "moinmoin" : [],
                    "pyblosxom" : ['PyBlosxom', 'pygments'],
                    "repozewho" : ["repoze.who>=1.0.10"],
                    "repozewhat" : ["repoze.who>=1.0.10", "repoze.what>=1.0.8"],
                    "repozepylons" : ["repoze.who>=1.0.10", "repoze.what>=1.0.8",
                                      "repoze.what_pylons>=1.0", 
                                      "repoze.what_quickstart>=1.0.6",
                                      "FormAlchemy", "fa.jquery>=0.6"],
                    "microsite" : ["Babel>=0.9.4", "ToscaWidgets>=0.9.4",
                                   "tw.forms>=0.9.3dev-20090122"],
                    "shenu" : [],
                    "sqlaval" : []
                    },
    include_package_data=True,
    entry_points="""
        [paste.paster_command]
        runner = shabti.commands:RunnerCommand
        migrate = shabti.commands:MigrateCommand
        model = shabti.commands:ModelCommand
        create_sql = shabti.commands:CreateSqlCommand
        drop_sql = shabti.commands:DropSqlCommand
        reset_sql = shabti.commands:ResetSqlCommand
        scaffold = shabti.commands:ScaffoldCommand [sqlaval]
        [paste.paster_create_template]
        shabti = shabti.template:ShabtiTemplate
        shabti_auth = shabti.template:ShabtiAuthTemplate
        shabti_auth_xp = shabti.template:ShabtiAuthXpTemplate
        shabti_auth_couchdb = shabti.template:ShabtiAuthCouchdbTemplate [couchdb]
        shabti_authplus = shabti.template:ShabtiAuthplusTemplate [authplus]
        shabti_auth_repozewho = shabti.template:ShabtiAuthRepozeWhoTemplate [repozewho]
        shabti_auth_repozewhat = shabti.template:ShabtiAuthRepozeWhatTemplate [repozewhat]
        shabti_auth_repozepylons = shabti.template:ShabtiAuthRepozePylonsTemplate [repozepylons]
        shabti_auth_rdfalchemy = shabti.template:ShabtiAuthRDFAlchemyTemplate [rdfal]
        shabti_formalchemy = shabti.template:ShabtiFormAlchemyTemplate [formalchemy]
        shabti_microsite = shabti.template:ShabtiMicroSiteTemplate [microsite]
        shabti_moinmoin = shabti.template:ShabtiMoinMoinTemplate [moinmoin]
        shabti_pyblosxom = shabti.template:ShabtiPyBlosxomTemplate [pyblosxom]
        shabti_quickwiki = shabti.template:ShabtiQuickWikiTemplate
        shabti_rdfalchemy = shabti.template:ShabtiRDFAlchemyTemplate [rdfal]
        shabti_couchdbkit = shabti.template:ShabtiCouchdbkitTemplate [couchdbkit]
        shabti_humanoid = shabti.template:ShabtiHumanoidTemplate [humanoid]
        shabti_shenu = shabti.template:ShabtiShenuTemplate [shenu]
    """)

