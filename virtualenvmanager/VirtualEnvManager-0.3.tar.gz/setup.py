import sys
from setuptools import setup, find_packages

version = "%i.%i" % sys.version_info[:2]
setup(
    name = "VirtualEnvManager",
    version = "0.3",
    packages = find_packages(),
    install_requires = ['virtualenv'],

    author = "Diez B. Roggisch",
    author_email = "deets@web.de",
    description = "A package to manage various virtual environments.",
    license = "PSF",
    keywords = "python virtualenv",
    entry_points = {
        'console_scripts': [
            'vem = vem.manager:main',
            'vem_python = vem.manager:python',
            'vem%s = vem.manager:main' % version,
            'vem_python%s = vem.manager:python' % version
        ],
    }
)
