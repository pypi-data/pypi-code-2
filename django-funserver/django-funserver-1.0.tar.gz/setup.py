from distutils.core import setup
import os


setup(name='django-funserver',
      version='1.0',
      description='FUNserver for Django',
      long_description=open(os.path.join(os.path.dirname(__file__), 'README')).read(),
      author='James Bennett',
      author_email='james@b-list.org',
      url='http://bitbucket.org/ubernostrum/django-funserver/',
      download_url='http://bitbucket.org/ubernostrum/django-funserver/downloads/django-funserver-1.0.tar.gz',
      packages=['funserver', 'funserver.management', 'funserver.management.commands'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )
