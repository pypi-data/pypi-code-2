from setuptools import setup
import os

AUTHOR = "Preston Timmons"
AUTHOR_EMAIL = "prestontimmons@gfa.org"
PACKAGE = "hgrecipe"
MODULE = "hgrecipe"
VERSION = "0.9"
DESCRIPTION = "Buildout recipe for cloning sources from a mercurial repository."


# Compile the list of packages available
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk(MODULE):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)

    prefix = dirpath[len(MODULE) + 1:]
    for f in filenames:
        if not f.endswith(".py") and not f.endswith(".pyc"):
            data_files.append(os.path.join(prefix, f))

setup(
    name=PACKAGE,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    package_dir={MODULE: MODULE},
    packages=packages,
    package_data={MODULE: data_files},
    classifiers=[
         'Intended Audience :: Developers',
         'Programming Language :: Python',
         'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points = {
        'zc.buildout': ['default = hgrecipe.recipe:Recipe'],
        'zc.buildout.uninstall': ['default = hgrecipe.recipe:uninstall'],
    },
    install_requires = ["Mercurial", "Mock==0.6.0"],
)
