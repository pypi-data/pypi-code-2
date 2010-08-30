from setuptools import setup, find_packages
from finddata import find_package_data

import os
execfile(os.path.join("tgwebservices", "release.py"))

setup(
    name="TGWebServices",
    version=version,
    
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    license=license,
    
    install_requires = [
        "TurboGears >= 1.0",
        "Genshi >= 0.3.4",
        "PEAK-Rules >= 0.5a1.dev-r2555",
    ],
    scripts = [],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='tgwebservices',
                                     package='tgwebservices'),
    keywords = [
        "turbogears.extension"
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        # if this is an application that you'll distribute through
        # the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Applications',
        
        # if this is a package that includes widgets that you'll distribute
        # through the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Widgets',
    ],
    test_suite = 'nose.collector',
    entry_points="""
    [python.templating.engines]
    wsautoxml = tgwebservices.xml_:AutoXMLTemplate
    """
    )
    
