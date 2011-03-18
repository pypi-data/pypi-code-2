import os
__requires__="TurboGears"
from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

packages=find_packages()
package_data = find_package_data(where='turboflot', package='turboflot')

setup(
    name="TurboFlot",
    version="0.2.0",
    description="A TurboGears widget for Flot, a jQuery plotting library",
    author="Luke Macken",
    author_email="lewk@csh.rit.edu",
    license="MIT",
    install_requires=[
        "TurboGears >= 1.0.3.2",
    ],
    scripts=[],
    data_files=[
        'turboflot/static/excanvas.min.js',
        'turboflot/static/jquery.colorhelpers.min.js',
        'turboflot/static/jquery.flot.crosshair.min.js',
        'turboflot/static/jquery.flot.image.min.js',
        'turboflot/static/jquery.flot.min.js',
        'turboflot/static/jquery.flot.navigate.min.js',
        'turboflot/static/jquery.flot.selection.min.js',
        'turboflot/static/jquery.flot.stack.min.js',
        'turboflot/static/jquery.flot.threshold.min.js',
        'turboflot/static/jquery.min.js',
        'turboflot/static/jquery.flot.pie.js',
        'turboflot/static/turboflot.css',
    ],
    zip_safe=False,
    packages=packages,
    package_data=package_data,
    keywords=[
        'turbogears.widgets',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
    ],
    entry_points = """
        [turbogears.widgets]
        turboflot = turboflot.widgets
    """
)
