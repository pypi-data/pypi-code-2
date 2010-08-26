# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='pyf.services',
    version='1.9.5',
    description='PyF Services is a web service, web-based IDE and scheduler for flow-based programming part of the PyF Framework.',
    author='htaieb, jonathan schemoul',
    author_email='he.taieb@gmail.com, jonathan.schemoul@gmail.com',
    url='http://pyfproject.org',
    install_requires=[
        "TurboGears2 >= 2.1a1",
        "Babel >=0.9.4",
        
        "toscawidgets >= 0.9.7.1",
        "tw.forms",
        
        "zope.sqlalchemy >= 0.4 ",
        "repoze.tm2 >= 1.0a4",
        
        "repoze.what-quickstart >= 1.0",
        
        "pyf>=1.0dev",
        "pyf.transport>=1.0dev",

        "pyjon.descriptors",
        "pyjon.utils",
        "pyjon.events",
        'pyjon.versionning',

        "pyf.componentized>=0.11dev",
        "pyf.components.adapters.standardtools>=0.4",
	"pyf.components.producers.descriptorsource",
        
        "tgext.admin>=0.3.3",
        "tgext.admin<=0.3.6",
        "tgext.crud>=0.3.2",
        "tgext.crud<=0.3.8",
	"sprox==0.6.6",
        
        "mercurial>=1.2",
        
        "tw.dynforms",
        
        "turbomail >= 3.0",

        "TGScheduler >= 1.6",
        
        "pygments",

        "pyf.station",

	"lxml>=2.2",
	"docutils"
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
