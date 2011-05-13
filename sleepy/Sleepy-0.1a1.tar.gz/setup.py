try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


version = "0.1a1"

long_description = """\
This is a CMS of sorts for the Pylons web framework.

Uses a YAML configuration file to generate/interact with Berkeley DBXML
databases through a RESTful web interface.

Also includes useful Javascript libraries (e.g. Fancybox).
"""

setup( name="Sleepy",
       version=version,
       description="A RESTful sort-of-CMS built primarily on Pylons and Berkeley DBXML",
       long_description=long_description,
       classifiers=[ "Development Status :: 3 - Alpha",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: MIT License",
                     "Programming Language :: Python",
                     "Programming Language :: JavaScript",
                     "Topic :: Internet :: WWW/HTTP",
                     "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
                     "Framework :: Paste",
                     "Framework :: Pylons" ],
        keywords="web wsgi",
        author="Julian Rosse",
        author_email="julian@helixbass.net",
#        url="http://helixbass.net/projects/sleepy",
        license="MIT",
        install_requires=[ "Pylons>=1.0",
                           "PIL",
                           "PyYAML",
                           "dbxml",
                           "gdata",
                           "lxml",
                           "mutagen",
                           "ordereddict",
                           "python-dateutil" ],
        zip_safe=False,
        entry_points="""\
                      [paste.paster_create_template]
                      sleepy=sleepy.pasties:SleepyTemplate
                     """,
        setup_requires=[ "hgtools" ],
        packages=find_packages( exclude=[ "ez_setup",
                                          "distribute_setup",
                                          "tests" ] ))
