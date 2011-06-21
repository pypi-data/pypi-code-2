from setuptools import setup
setup(
    name="crawlidator",
    version="0.1",
    author="Chris Wesseling",
    author_email="chris.wesseling@cwi.nl",
    url="https://bitbucket.org/charstring/crawlidator",
    description="A validator that crawls your sitemap.xml",
    classifiers=['Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking',
        'Topic :: Utilities'],
    license="BSD",

    keywords="validation sitemap.xml",
    packages=['crawlidator'],
    package_data={'crawlidator': ['dtd/*']},
    test_suite='tests',
    scripts=['bin/crawlidator'],
    zip_safe=False,
    install_requires=['PyXML>=0.8.4',
                      'egenix-mx-base>=3.1.2',
                      'argparse'
                     ]
    )
