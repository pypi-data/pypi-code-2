from distutils.core import setup
 
# modified version no cherrypy reliance
setup(
    name="django-wsgiserver",
    version="0.6.5",
    description="""django-wsgiserver installs a web server for Django using CherryPy's WSGI server.""",
    author="""Peter Baumgartner Chris Lee-Messer the authors of CherryPy""",
    author_email="pete@lincolnloop.com, chris@lee-messer.net",
    # from README.rst
    long_description="""
Summary
-------

django-wsgiserver is a django app for serving Django sites via
CherryPy's excellent, production ready, pure-python web server without needing to
install all of Cherrypy_.  Note that Cherrypy names its server "wsgiserver" but
it is actually a full-blown, multi-threaded http/https web server which has been
used on production sites alone, or more often proxied behind a something like
Apache or nginx.

Uses
----
The wsgiserver component has been used for years in production.  Peter
Baumgartner noted that it solved problems for him on memory on a memory-limited
VPS hosted site [#]_.  Performance-wise it does well: it can serve up thousands
of requests per second [Piel2010].

I haven't used django-wsgiserver for production myself (yet) as daemonized
modwsgi_ and uwsgi_ have served me well. I use it all the time though during
development. It's my "pocket-sized" server. completely written in python and it
gives me an instant approximation of the final production environment I use.  In
some ways, it's much better than the development server which is built into
django.  It's noticeable when I have pages that do multiple ajax calls and the
built-in runserver hangs.  I just stop the built-in server, and then do 

::

   $ manage.py runwsgiserver

and reload my browser page and the problem is fixed.  It's also useful to see if
some weird effect is being caused by runserver's process of loading the settings
twice.

This project is a slight modification of code form Peter Baumgartner code (see `Peter's
blog post`_) Peter and others did the work of creating a management command.
I've added a few small improvements from my point of view: It doesn't require
installing cherrypy separately. It uses the same port as the development server
(8000) so I don't need to re-enter my testing url in my browser, and it works by
default with OS's like Mac OS 10.6 and Ubuntu 10.04 which prefer binding
localhost to an ip6 address.

Feature list
------------
- multi-threaded production ready webserver for low to medium traffic sites
- pure python
- setuptools/pip installable (so install right in virtualenv)
- small memory footprint
- by default replaces mimics the django built-in server, serves admin media by
  default for easy development

Planned features
---------------
- serve static media automatically
- improve autoreload of changed files during development

  
Requirements
------------
To get started using the server, you need nothing outside of django itself and
the project code that you would like to serve up. However, for ssl support, you
may need PyOpenSSL--though the new cherrypy server includes support for using the
python built-in ssl module depending on which version of python you are using.

Installation
------------
To install, django-wsgiserver follows the usual pattern for a django python application.  You have several options

1. pip install django-wsgiserver OR
2. easy_install django-wsgiserver
3. If you would like to use the latest possible version, you can use pip and mercurial checkout from bitbucket

::

   pip install -e hg+https://cleemesser@bitbucket.org/cleemesser/django-cherrypy-wsgiserver#egg=django-wsgiserver

4. Alternatively you can download the code and install it so that django_wsgiserver is on your PYTHONPATH

After you used one of the methods above, you need to add django_wsgiserver to your INSTALLED_APPS in your django project's settings file

Usage
-----
To see how to run the server as a management command, run::

    $ python manage.py runwsgiserver help  
    
from within your project directory. You'll see something like what's below::

  Run this project in CherryPy's production quality http webserver.
  Note that it's called wsgiserver but it is actually a complete http server.

    runwsgiserver [options] [wsgi settings] [stop]

    Optional CherryPy server settings: (setting=value)
      host=HOSTNAME         hostname to listen on
			    Defaults to 127.0.0.1,
			    (set to 0.0.0.0 to bind all ip4 interfaces or :: for
			    all ip6 interfaces)
      port=PORTNUM          port to listen on
			    Defaults to 8000
      server_name=STRING    CherryPy's SERVER_NAME environ entry
			    Defaults to localhost
      daemonize=BOOL        whether to detach from terminal
			    Defaults to False
      pidfile=FILE          write the spawned process-id to this file
      workdir=DIRECTORY     change to this directory when daemonizing
      threads=NUMBER        Number of threads for server to use
      ssl_certificate=FILE  SSL certificate file
      ssl_private_key=FILE  SSL private key file
      server_user=STRING    user to run daemonized process
			    Defaults to www-data
      server_group=STRING   group to daemonized process
			    Defaults to www-data
      adminserve=True|False  Serve the admin media automatically. Useful in
                             development. Defaults to True so turn to False if
                             using in production.

    Examples:
      Run a "standard" CherryPy server server
	$ manage.py runwsgiserver

      Run a CherryPy server on port 80
    $ manage.py runwsgiserver port=80

  Run a CherryPy server as a daemon and write the spawned PID in a file
    $ manage.py runwsgiserver daemonize=true pidfile=/var/run/django-cpwsgi.pid

      Run a CherryPy server using ssl with test certificates located in /tmp
    $ manage.py runwsgiserver ssl_certificate=/tmp/testserver.crt ssl_private_key=/tmp/testserver.key


Notes
-----

If you want to use an installed version of Cherrypy--perhaps because you now have
a more recent version, you only need to change one line of code in (around line
177) of django_wsgiserver/management/commands/run_wsgiserver.py::

    from django_wsgiserver.wsgiserver import CherryPyWSGIServer as Server
    #from cherrypy.wsgiserver import CherryPyWSGIServer as Server

Just comment out the import from django_wsgiserver.wsgiserver and uncomment the import from cherrypy.wsgiserver to make the switch.

To do
-----
- looking at settings for serving static media automatically see [arteme2009; dev-picayune2008]
[x] get in touch with Peter/see if a merge would be desirable. email: no merge.
- I should probably just add a switch to allow use of the native cherrypy install
[x] upload to the cheeseshop/pypi at some point. Flubbed it first few times but
I'm getting there.


Changelog
---------
- 0.6.3 - see if I can get the download to finally include all the
packages--didn't have wsgiserver! 
- added test project in tests/ directory
- got tired of typing run_cp_wsgiserver so did a rename so I could use runwsgiserver instead.
- updated wsgiserver to svn r2680 (matches cherrypy version 3.2 beta+). This fixes some bugs and gives better python 2.6 support.  This version of cherrypy will also support python 3.x for whenever django starts supporting it.


- use port 8000 as with django devserver rather than Cherrypy's default 8088

- adapted defaults host=127.0.0.1 in order to work with ip4 by default.  This
  addresses an issue I first noticed on mac OS 10.6 and later on ubuntu 10.04
  where ip6 is active by default. Can get around this by adjusting the host
  option.  For binding all ip4 interfaces, set to 0.0.0.0. For all ip6 interfaces
  I believe you use '::' You can also bind a specific interface by specifying
  host=<specific ip address>  See http://www.cherrypy.org/ticket/711
  
- switched code to use run_cp_wsgiserver instead of runcpserver





Acknowledgments and References
------------------------------
Many thanks to Peter and lincolnloop for describing how to do this and writing the code.

Peter acknowledged idea and code snippets borrowed from Loic d'Anterroches, adapted to run as a management command

Note, there is also similar code on PyPi and at http://hg.piranha.org.ua/cpserver/ maintained by Alexander Solovyov

The latest version of the cherrypy wsgiserver can be retrieved with::

    svn co http://svn.cherrypy.org/trunk/cherrypy/wsgiserver

Peter hosts his code at http://github.com/lincolnloop/django-cpserver 

.. [#] For example `Peter's blog post`_ describes using django_cpserver on a VPS.

.. _`Peter's blog post`: http://lincolnloop.com/blog/2008/mar/25/serving-django-cherrypy/

.. _Cherrypy: http://www.cherrypy.org/

.. _[Piel2010] : http://nichol.as/benchmark-of-python-web-servers Nicholas Piel provides a nice comparison of different wsgi servers. Cherrypy's wsgiserver does quite respectably, demonstrating > 2000 requests/sec even at high load for http 1.0 connections with good response latencies.  It does reasonably with http 1.1 connections as well.

.. _modwsgi : http://code.google.com/p/modwsgi/

.. _uwsgi : http://projects.unbit.it/uwsgi/

.. _[dev-picayune2008] : http://www.devpicayune.com/entry/hosting-django-with-cherrypy-wsgi-server Using middleware to add logging and serve the admin media files.  Paste TransLogger.

.. _[arteme2009] : http://www.arteme.fi/2009/02/26/django-cherrypy-dev-server-and-static-files/  More on serving admin files and static files in general with wsgiserver.

""",
    url="http://bitbucket.org/cleemesser/django-cherrypy-wsgiserver/downloads",
    packages=[
        "django_wsgiserver",
        "django_wsgiserver.management",
        "django_wsgiserver.management.commands",
        "django_wsgiserver.wsgiserver",
    ],
    classifiers=['Framework :: Django',
                 'Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'License :: OSI Approved :: BSD License',
                 'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
                 'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
                 ],
    )

