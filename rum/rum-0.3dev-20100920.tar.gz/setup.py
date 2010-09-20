from setuptools import setup, find_packages
import sys, os

execfile(os.path.join("rum", "release.py"))

setup(name='rum',
    version=__VERSION__,
    description="RESTful web interface generator",
    long_description="""\
    """,
    classifiers=[],
    keywords='toscawidgets crud wsgi sqlalchemy',
    author=__AUTHOR__,
    author_email='info@python-rum.org',
    url='http://python-rum.org/',
    license=__LICENSE__,
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    test_suite = "nose.collector",
    zip_safe=False,
    dependency_links = [
        # Until/if this is ever registered at PyPI
        #'http://pypi.python-rum.org/custom/index/EggTranslations/',
    ],
    install_requires=[
        "PEAK-Rules>=0.5a1.dev-r2569",
        "WebFlash >= 0.1a7",
        "FormEncode >= 1.1",
        "repoze.tm2 >= 1.0a1",
        "ToscaWidgets >= 0.9.3",
        "prioritized_methods >= 0.2.1",
        "Genshi >= 0.5.1",
        "TurboJson >= 1.2",
        "simplejson >= 2.0.8",
        "configobj >= 4.5.3",
        "Paste >= 1.7.1",
        "PasteScript >= 1.6.3",
        "PasteDeploy >= 1.3.2",
        "WebOb >= 0.9.7.1",
        "Routes >= 1.10",
        "Babel >= 0.9.4",
        "EggTranslations >= 1.2.1",
        "rum.component",
        "rum-generic",
        "rum-policy"
    ],
    extras_require = {
        'dev': ['ipython', 'sphinx'],
    },
    tests_require = ['WebTest', 'WebError', 'nose', 'coverage', 'Mako',
                     'BeautifulSoup'],
    message_extractors = {'rum': [
        ('**.py', 'python', None),
        ('**.html', 'genshi', {'extract_text':False}),
        ]},
    entry_points="""
    [console_scripts]
    rum_i18n_update = rum.i18n:main

    [paste.app_factory]
    main = rum.wsgiapp:make_app

    [toscawidgets.widgets]
    widgets = rum.widgets

    [rum.controllerfactory]
    default = rum:ControllerFactory

    [rum.repositoryfactory]
    default = rum:RepositoryFactory

    [rum.viewfactory]
    default = rum:ViewFactory

    [rum.jsonencoder]
    default = rum.json:JsonEncoder

    [rum.renderers]
    mako = rum.templating.mako_renderer:MakoRenderer
    genshi = rum.templating.genshi_renderer:GenshiRenderer
    chameleon-genshi = rum.templating.chameleon_renderer:ChameleonGenshiRenderer
    genshi-xml = rum.templating.genshi_renderer:GenshiXMLRenderer

    [rum.policy]
    default = rum.policy:DummyPolicy

    [rum.router]
    default = rum.router:RumRouter

    [rum.translator]
    default = rum.i18n:RumTranslator



    # These are just for the tests
    [test.robot.weapon]
    axe = rum.tests.test_component:Axe
    """,
    )
