from distutils.core import setup
import os


AUTHOR = "Preston Timmons"
AUTHOR_EMAIL = "prestontimmons@gmail.com"
PACKAGE_NAME = "django-magneto"
MODULE_NAME = "magneto"
VERSION = "0.9.0"
DESCRIPTION="A content and template management application for Django."
URL="http://bitbucket.org/prestontimmons/django-magneto/src"


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk(MODULE_NAME):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[6:] # Strip module name
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    package_dir={MODULE_NAME: MODULE_NAME},
    packages=packages,
    package_data={MODULE_NAME: data_files},
    classifiers=[
       'Environment :: Web Environment',
       'Framework :: Django',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: BSD License',
       'Programming Language :: Python',
    ],
)
