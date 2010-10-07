import os

from setuptools import setup, find_packages

from htmlsanitizer import __version__ as version

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)
for dirpath, dirnames, filenames in os.walk('htmlsanitizer'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[14:] # Strip "htmlsanitizer/" or "htmlsanitizer\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name = "django-htmlsanitizer",
      version=version,
      description = "@TODO",
      long_description='\n\n'.join([read("README"), read("CHANGELOG")]),
      author = 'Co-Capacity',
      author_email = 'django-htmlsanitizer@co-capacity.org',
      url='http://pypi.python.org/pypi/django-htmlsanitizer',
      package_dir={'htmlsanitizer': 'htmlsanitizer'},
      packages=packages,
      package_data={'htmlsanitizer': data_files},
      install_requires = ['setuptools', 'BeautifulSoup'],
      zip_safe=False,
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP',
      ]
)
