import os
from setuptools import setup

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

PACKAGE = 'urlauth'

for dirpath, dirnames, filenames in os.walk(PACKAGE):
    for i, dirname in enumerate(dirnames):
        if dirname in ['.', '..']:
            del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[len(PACKAGE) + 1:] # Strip package directory + path separator
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(
    version = '0.1.3',
    description = 'Django application for user authentication with key in hypertext link',
    author = 'Grigoriy Petukhov',
    author_email = 'lorien@lorien.name',
    url = 'http://bitbucket.org/lorien/django-urlauth/',
    name = 'django-urlauth',

    packages = packages,
    package_data = {'urlauth': data_files},

    license = "BSD",
    keywords = "django application authentication authorization",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
