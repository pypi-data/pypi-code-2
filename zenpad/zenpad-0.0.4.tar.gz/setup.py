import os
from setuptools import setup

PACKAGE = 'zenpad'
VERSION = '0.0.4'

if __name__ == '__main__':
    # Compile the list of packages available, because distutils doesn't have
    # an easy way to do this.
    packages, data_files = [], []
    root_dir = os.path.dirname(__file__)
    if root_dir:
        os.chdir(root_dir)

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
        name = PACKAGE,
        version = VERSION,
        description = 'Tree-structured notepad',
        long_description = open(os.path.join(
            os.path.dirname(__file__), 'README.rst')).read(),
        author = 'Imbolc',
        author_email = 'imbolc@imbolc.name',
        url = 'http://bitbucket.org/imbolc/zenpad/',
        packages = packages,
        package_data = {'zenpad': data_files},
        entry_points = {
            'gui_scripts': [
                'zenpad = zenpad.zenpad:main',
            ]
        },
        license = "BSD",
        classifiers = [
            "Programming Language :: Python",
            "License :: OSI Approved :: MIT License",
            "Development Status :: 4 - Beta",
            "Environment :: X11 Applications :: Qt",
            "Intended Audience :: End Users/Desktop",
            "Natural Language :: Russian",
            "Topic :: Text Editors",
        ],
    )
