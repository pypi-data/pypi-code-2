from setuptools import setup, find_packages

setup(
    name='wdmmgext',
    version='0.1',
    description='Where Does My Money Go (WDMMG) Extension Code',
    author='Open Knowledge Foundation (Where Does My Money Go)',
    author_email='wdmmg@okfn.org',
    url='http://www.wheredoesmymoneygo.org/',
    install_requires=[
        "datapkg>=0.7"
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    entry_points="""
    [wdmmg.load]
    israel = wdmmgext.load.israel:load
    barnet = wdmmgext.load.barnet:load
    dfid = wdmmgext.load.dfid:load
    cofog = wdmmgext.load.cofog:load
    cra = wdmmgext.load.cra:load
    cra2010 = wdmmgext.load.cra2010:load
    ordnance = wdmmgext.load.ordnance:load
    gla = wdmmgext.load.gla:load
    departments = wdmmgext.load.departments:load
    bmf = wdmmgext.load.bmf:load
    uganda = wdmmgext.load.uganda:load
    spain = wdmmgext.load.spain:load
    fts = wdmmgext.load.fts:load
    """,
)
