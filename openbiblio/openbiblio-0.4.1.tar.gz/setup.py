from setuptools import setup, find_packages

version = "0.4.1"

setup(
    name='openbiblio',
    version=version,
    description='RDF Open Source Bibliographic Catalogue System',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='http://bibliographica.org/',
    license="AGPL",
    install_requires=[
        'Pylons>=1.0',
        'Genshi>=0.5',
    	'pymarc',
    	'swiss==0.3',
        'ordf>=0.34',
        'rdflib>=3.0',
        'ontosrv',
        'python-openid>=2.2.5', 
        'repoze.who>=1.0.0,<1.99.99',
        'repoze.who.plugins.openid>0.5',
        'autoneg',
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'openbiblio': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'openbiblio': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = openbiblio.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [paste.paster_command]
    fetch = openbiblio.commands.fetch:Fetch
    fixtures = openbiblio.commands:Fixtures
    cleandb = openbiblio.commands:CleanDB
    updateusers = openbiblio.commands:UpdateUsers
    materialise = openbiblio.commands.materialise:Materialise
    
#    lenses = openbiblio.commands:Lenses
#    load_marc = openbiblio.commands.marc_loader:Loader
#    edit_marc = openbiblio.commands.marc_editor:Editor
#    dedup = openbiblio.commands.dedup:DeDup

    [ordf.namespace]
    openbiblio = openbiblio.lib.namespace:init_ns

    [ordf.xapian]
    index = openbiblio.lib.xapindex:index_store
    search = openbiblio.lib.xapindex:search
    """,
)
