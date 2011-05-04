from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound

import sys
import os

if sys.version_info < (2, 3):
    raise SystemExit("Python 2.3 or later is required")

execfile(os.path.join("turbogears", "release.py"))

# setup params
install_requires = [
    "CherryPy >= 2.3.0, < 3.0.0alpha",
    "ConfigObj >= 4.3.2",
    "DecoratorTools >= 1.4",
    "FormEncode >= 0.7.1",
    "PasteScript >= 1.6.2",
    "RuleDispatch >= 0.5a0.dev-r2303",
    "setuptools >= 0.6c2",
    "simplejson >= 1.3",
    "TurboCheetah >= 1.0",
    # TurboJson >= 1.2 uses PEAK-Rules
    "TurboJson >= 1.1.4, < 1.2",
    "TurboKid >= 1.0.4",
]

exp = ["TGFastData"]

future = [
    "Elixir >= 0.4.0",
    "Genshi >= 0.4.4",
]

sqlobject = [
    "SQLObject >= 0.10.1",
]

if sys.version_info < (2, 4):
    sqlalchemy = [
        # SQLAlchemy >= 0.5 does not support Py 2.3
        "SQLAlchemy >= 0.3.10, < 0.5.0alpha",
        ]
else:
    sqlalchemy = [
        "SQLAlchemy >= 0.3.10",
    ]

testtools =  [
    "nose >= 0.9.3",
]

tgtesttools = testtools

if sys.version_info < (2, 5):
    tgtesttools.extend([
            # Python < 2.5 does not include SQLite
            "pysqlite",
        ])

develop_requires = (install_requires + future + tgtesttools + sqlalchemy +
    sqlobject)


setup(
    name="TurboGears",
    version=version,
    author=author,
    author_email=email,
    download_url="http://www.turbogears.org/download/filelist.html",
    dependency_links=[
        "http://files.turbogears.org/eggs/",
        ],
    license=license,
    description="front-to-back rapid web development",
    long_description="""\
Front-to-back rapid web development
===================================

TurboGears brings together four major pieces to create an
easy to install, easy to use web megaframework. It covers
everything from front end (MochiKit JavaScript for the browser,
Kid/Genshi/Mako/Cheetah for templates in Python) to the controllers
(CherryPy) to the back end (SQLAlchemy or SQLObject).

The TurboGears project is focused on providing documentation
and integration with these tools without losing touch
with the communities that already exist around those tools.

TurboGears is easy to use for a wide range of web applications.

The latest development version is available in the
`TurboGears subversion repository`_.

Our `mailing list`_ is lively and helpful, don't hesitate to
send your questions there, we will try to help you find out
a solution to your problem.

.. _mailing list:
    http://groups.google.com/group/turbogears

.. _TurboGears subversion repository:
    http://svn.turbogears.org/trunk#egg=turbogears-dev
""",
    url="http://www.turbogears.org",
    zip_safe=False,
    install_requires = install_requires,
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={"thirdparty": ["*"]},
    entry_points = """
    [console_scripts]
    tg-admin = turbogears.command:main

    [distutils.commands]
    docs = turbogears.docgen:GenSite

    [paste.paster_create_template]
    tgbase = turbogears.command.quickstart:BaseTemplate
    turbogears = turbogears.command.quickstart:TurbogearsTemplate
    tgbig = turbogears.command.quickstart:TGBig
    tgwidget = turbogears.command.quickstart:TGWidgetTemplate

    [turbogears.command]
    quickstart = turbogears.command.quickstart:quickstart
    sql = turbogears.command.base:SQL
    shell = turbogears.command.base:Shell
    toolbox = turbogears.command.base:ToolboxCommand
    update = turbogears.command.quickstart:update
    i18n = turbogears.command.i18n:InternationalizationTool
    info = turbogears.command.info:InfoCommand

    [turbogears.identity.provider]
    sqlobject = turbogears.identity.soprovider:SqlObjectIdentityProvider
    sqlalchemy= turbogears.identity.saprovider:SqlAlchemyIdentityProvider

    [turbogears.extensions]
    identity = turbogears.identity.visitor
    visit = turbogears.visit

    [turbogears.visit.manager]
    sqlobject = turbogears.visit.sovisit:SqlObjectVisitManager
    sqlalchemy = turbogears.visit.savisit:SqlAlchemyVisitManager

    [turbogears.toolboxcommand]
    widgets = turbogears.toolbox.base:WidgetBrowser
    shell = turbogears.toolbox.shell:WebConsole
    admi18n = turbogears.toolbox.admi18n:Internationalization
    designer = turbogears.toolbox.designer:Designer
    info = turbogears.toolbox.base:Info
    catwalk = turbogears.toolbox.catwalk:CatWalk

    """,
    extras_require = {
        "exp" : exp,
        "sqlobject" : sqlobject,
        "sqlalchemy" : sqlalchemy,
        "future" : future,
        "testtools" : testtools,
        "tgtesttools" : tgtesttools,
        "develop" : develop_requires
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    test_suite = 'nose.collector',
)
