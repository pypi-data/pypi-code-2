try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.8'
try:
    from mercurial import ui, hg, error
    repo = hg.repository(ui.ui(), ".")
    ver = repo[version]
except ImportError:
    pass
except error.RepoLookupError:
    tip = repo["tip"]
    version = version + ".%s.%s" % (tip.rev(), tip.hex()[:12])
except: # can not be allowed to blow up on build
    pass

setup(
    name='ontosrv',
    version=version,
    description='ORDF Ontology Service',
    author='William Waites',
    author_email='william.waites_at_okfn.org',
    url='',
    install_requires=[
        "Pylons>=0.9.7",
        "Genshi>=0.4",
        "Routes>=1.12",
        "ordf>=0.5",
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'ontosrv': ['i18n/*/LC_MESSAGES/*.mo']},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = ordf.onto.config.middleware:make_app

    [paste.app_install]
    main = ordf.onto.websetup:Installer
    """,
)
