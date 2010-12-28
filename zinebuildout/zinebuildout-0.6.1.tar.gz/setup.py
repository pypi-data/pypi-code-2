from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zinebuildout',
      version='0.6.1',
      description="Deploy the Zine blog engine with Paste in a buildout",
      long_description=read('README.txt'),
      keywords='zine buildout paste',
      author='Christophe Combelles',
      author_email='ccomb@gorfou.fr',
      url='https://cody.gorfou.fr/hg/zinebuildout',
      license='BSD',
      # Get more from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   'Intended Audience :: Information Technology',
                   'Framework :: Buildout',
                   'Framework :: Paste',
                   'License :: OSI Approved :: BSD License',
                   ],

      packages=['zinebuildout'],
      package_dir={'zinebuildout':'zinebuildout'},
      install_requires=['setuptools'],
      include_package_data=True,
      zip_safe=False,
      entry_points = """
      [paste.app_factory]
      main = zinebuildout.paste:app_factory
      """
      )
