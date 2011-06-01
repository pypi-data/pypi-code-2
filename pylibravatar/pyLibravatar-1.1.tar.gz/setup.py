from distutils.core import setup

setup(
    name = 'pyLibravatar',
    version = '1.1',
    description = 'Python module for Libravatar',
    author = 'Francois Marier',
    author_email = 'francois@libravatar.org',
    url = 'https://launchpad.net/pylibravatar',
    py_modules = ['libravatar'],
    license = 'MIT',
    keywords = ['libravatar', 'avatars', 'autonomous', 'social', 'federated'],
    requires = ['pydns'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
PyLibravatar is an easy way to make use of the federated `Libravatar`_
avatar hosting service from within your Python applications.

See the `project page`_ for the bug tracker and downloads.

.. _Libravatar: http://www.libravatar.org/
.. _project page: https://launchpad.net/pylibravatar
"""
    )
