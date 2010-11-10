from setuptools import setup, find_packages
import os

version = '0.1'

setup(
    name='collective.geo.mapcontent',
    version=version,
    description="Map content type for collective.geo (use c.g/MapWidget and c.g.openlayers)",
    long_description=open("README.txt").read() + "\n" +
    open(os.path.join("collective", "geo", "mapcontent", "README.txt")).read() + "\n" +
    open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
    "\n"
    ,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='',
    author='Mathieu PASQUET <kiorky@cryptelium.net>',
    author_email='kiorky@cryptelium.net',
    url='http://pypi.python.org/pypi/collective.geo.mapcontent',
    license='GPL',
    namespace_packages=['collective', 'collective.geo'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'plone.app.z3cform',
        'collective.geo.openlayers',
        'collective.geo.settings',
        'collective.geo.MapWidget',
    ],
    packages = find_packages('.'),
    entry_points="""
    # -*- entry_points -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
    setup_requires=["PasteScript"],
    paster_plugins=["ZopeSkel"],

)
