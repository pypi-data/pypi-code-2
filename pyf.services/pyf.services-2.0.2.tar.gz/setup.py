# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='pyf.services',
    version='2.0.2',
    description='PyF Services is a web service, web-based IDE and scheduler for flow-based programming part of the PyF Framework.',
    author='htaieb, jonathan schemoul',
    author_email='he.taieb@gmail.com, jonathan.schemoul@gmail.com',
    url='http://pyfproject.org',
    install_requires=[
        # -- TG-related deps -------------------------
        "TurboGears2 >= 2.1",
        "TGScheduler >= 1.6.2",
        "tgext.admin >= 0.3.3",
        "tgext.admin <= 0.3.6",
        "tgext.crud >= 0.3.2",
        "tgext.crud <= 0.3.8",
        "sprox == 0.6.6",
	"SQLAlchemy < 0.7", # we need this because of a limitation of sprox. fix TBD

        "toscawidgets >= 0.9.7.1",
        "tw.forms",
        "tw.dynforms",

        "pylons >= 1.0",

        "zope.sqlalchemy >= 0.4 ",

        "repoze.tm2 >= 1.0a4",
        "repoze.what-quickstart >= 1.0",
        "repoze.what-pylons >= 1.0",

        "Babel >= 0.9.4",

        # -- Misc deps -------------------------------
        "lxml >= 2.2",

        "docutils",
        "pygments",

        "turbomail >= 3.0",

        "mercurial >= 1.2",

        "pyjon.descriptors",
        "pyjon.utils >= 0.3",
        "pyjon.events ",
        'pyjon.versionning >= 0.4.2',

        # -- the PyF stack ---------------------------
        "pyf.dataflow >= 2.0",
        "pyf.manager >= 2.0",
        "pyf.splitter >= 2.0",
        "pyf.warehouse >= 2.0",
        
        "pyf.transport >= 2.0",
        "pyf.componentized >= 2.0",
        "pyf.components.adapters.standardtools >= 1.0",
        "pyf.components.producers.descriptorsource >= 0.5",
        "pyf.station >= 2.0",
        ],
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['pyf'],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    zip_safe=False,
    package_data={'pyf/services': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'pyf/services': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = pyf.services.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [console_scripts]
    pyfservices-setup = pyf.services.websetup:setup_app_command
    """,
)
