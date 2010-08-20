from setuptools import setup, find_packages
import sys, os

version = '0.1'

try:
    from mercurial import ui, hg, error
    repo = hg.repository(ui.ui(), ".")
    ver = repo[version]
except ImportError:
    pass
except error.RepoLookupError:
    tip = repo["tip"]
    version = version + ".%s.%s" % (tip.rev(), tip.hex()[:12])
except error.RepoError:
    pass

setup(
    name='unstats_rdf',
    version=version,
    description="RDF API for UN Statistical Division Data",
    long_description="""\
RDF API for UN Statistical Division Data""",
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="unstats rdf",
    author='Open Knowledge Foundation',
    author_email='okfn-help@lists.okfn.org',
    url="http://pypi.python.org/pypi/unstats_rdf_data",
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        "datapkg",
    ],
    install_requires=[
        "Paste",
        "setuptools",
        "ordf",
    ],
    entry_points = """
    """,
)
