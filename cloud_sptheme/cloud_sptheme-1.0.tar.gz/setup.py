"""
cloud_sptheme setup script
"""
#=========================================================
#init script env
#=========================================================
import sys,os
from os.path import abspath, join
root_path = abspath(join(__file__, ".."))
os.chdir(root_path)
lib_path = '.'
#=========================================================
#imports
#=========================================================
from setuptools import setup, find_packages
#=========================================================
#setup
#=========================================================
setup(
    #package info
    packages = find_packages(where=lib_path),
    package_data = { "cloud_sptheme": ["themes/*/*.*", "themes/*/static/*.*"] },
    zip_safe=False,

    install_requires=[ "sphinx>=1.0"],

    # metadata
    name = "cloud_sptheme",
    version = "1.0",
    author = "Eli Collins",
    author_email = "elic@assurancetechnologies.com",
    description = "a nice sphinx theme named 'Cloud', and some related extensions",
    long_description="""\
This is a small package containing a Sphinx theme named "Cloud",
along with some related Sphinx extensions. To see an example
of the theme in action, check out it's documentation
at `<http://packages.python.org/cloud_sptheme>`_.
    """,
    license = "BSD",
    keywords = "sphinx extension theme",
    url = "https://bitbucket.org/ecollins/cloud_sptheme",
    download_url = "http://pypi.python.org/pypi/cloud_sptheme",
    classifiers=[
        'Development Status :: 4 - Beta',
        #there should be a Framework::Sphinx::Extension classifier :)
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ]
)
#=========================================================
#EOF
#=========================================================
