from distutils.core import setup
 
# modified version no cherrypy reliance
setup(
    name="django-wsgiserver",
    version="0.6.7",
    description="""django-wsgiserver installs a web server for Django using CherryPy's WSGI server.""",
    author="""Peter Baumgartner Chris Lee-Messer the authors of CherryPy""",
    author_email="pete@lincolnloop.com, chris@lee-messer.net",
    # from README.rst
    long_description=open('README.rst').read(),
    url="http://bitbucket.org/cleemesser/django-cherrypy-wsgiserver/downloads",
    packages=[
        "django_wsgiserver",
        "django_wsgiserver.management",
        "django_wsgiserver.management.commands",
        "django_wsgiserver.wsgiserver",
    ],
    # package_data
    # data_files=[],# where to put test certs
    classifiers=['Framework :: Django',
                 'Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'License :: OSI Approved :: BSD License',
                 'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
                 'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
                 ],
    )

