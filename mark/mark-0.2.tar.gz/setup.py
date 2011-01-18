from setuptools import setup, find_packages
import sys, os

version = '0.2'
requirements=[
    "rdflib",
    ]

if isinstance(sys.version_info, tuple):
        requirements.append("argparse")
else:
    if sys.version_info.major == 2 and sys.version_info.minor < 7:
        requirements.append("argparse")

setup(
    name='mark',
    version=version,
    description="RDF Bookmarking Utilities",
    long_description="""\
RDF Bookmarking Utilities""",
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="rdf rdflib",
    author='Open Knowledge Foundation',
    author_email='okfn-help@lists.okfn.org',
    url="http://packages.python.org/mark/",
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    entry_points="""
        # -*- Entry points: -*-
        [console_scripts]
        mark=mark.command:mark
        marq=mark.command:marq
    """,
)
