from setuptools import setup, find_packages
import sys, os

install_requires = ['PasteDeploy']
if sys.version_info[:2] < (2, 6):
    install_requires += ['multiprocessing']

version = '0.3'

setup(name='ReloadWSGI',
      version=version,
      description="Robust WSGI auto-reloading for development.",
      long_description="""\

Replacement for 'paster serve --reload config.ini'.

Reload a WSGI application on source change. Keep the old code alive
when the change has syntax errors. Never close the socket, never refuse
a connection.

As of version 0.3, ReloadWSGI also supports reloading a server specified
in the config file. This is appropriate for wsgi servers such as
mongrel2_wsgi which are able to support two concurrent instances
without stepping on each other's network connection. Once ReloadWSGI
confirms the second server can load without throwing e.g. a syntax error,
the original server quits and Mongrel2's automatic load balancing
sends requests to the newer instance.


PID 4197 notifies us of a change in quux.py ::

    quux.py changed; reloading...
    {'status': 'changed', 'pid': 4197}


Oh no! We accidentally typed "foobar" instead of "import foobar"! ::

    Process Process-4:
    Traceback (most recent call last):
     ...
      File "quux.py", line 6, in <module>
        foobar
    NameError: name 'foobar' is not defined


Can we visit our site? YES!::

    127.0.0.1 - - [03/Mar/2010 09:41:52] "GET /orders HTTP/1.1" 200 2345


PID 4197 notifies us of /another/ change in quux.py ::

    quux.py changed; reloading...
    {'status': 'changed', 'pid': 4197}


We've fixed our problem. Once the new process loads, the old process
quits silently ::

    09:42:39,789 DEBUG [quux.run] App started.
    {'status': 'loaded', 'pid': 4354}
              
      """,
      classifiers=[
          "Intended Audience :: Developers",
          "Topic :: Internet :: WWW/HTTP :: WSGI",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License",
          ],
      keywords='wsgi',
      author='Daniel Holth',
      author_email='dholth@fastmail.fm',
      url='http://bitbucket.org/dholth/reloadwsgi/',
      license='MIT',
      py_modules=['reloadwsgi'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
# -*- Entry points: -*-
[console_scripts]
reloadwsgi = reloadwsgi:main
      """,
      )
