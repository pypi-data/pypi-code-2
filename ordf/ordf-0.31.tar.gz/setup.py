from setuptools import setup, find_packages
import sys, os

version = '0.31'

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
    name='ordf',
    version=version,
    description="Open Knowledge Foundation RDF",
    long_description="""\
Open Knowledge Foundation RDF Library""",
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Paste",
        "Framework :: Pylons",
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
    keywords="rdf rdflib provenance messaging",
    author='Open Knowledge Foundation',
    author_email='okfn-help@lists.okfn.org',
    url="http://ordf.org/",
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Paste",
        "setuptools",
        "rdflib",
        #"carrot", carrot is an optional dependency
        "pairtree",
    ],
    entry_points="""
        # -*- Entry points: -*-
        [console_scripts]
        ordf=ordf.command:ordf
        ordf_load=ordf.command:load_rdf
        fresnel=ordf.vocab.fresnel:render

        [ordf.handler]
        null=ordf.handler:HandlerPlugin
        pairtree=ordf.handler.pt:PairTree
        rdflib=ordf.handler.rdf:RDFLib
        fourstore=ordf.handler.rdf:FourStore
        xapian=ordf.handler.xap:Xapian
        redis=ordf.handler.cache:Redis
        rabbit=ordf.handler.queue:RabbitQueue
        fuxi=ordf.handler.fuxi:FuXiReasoner
    """,
)
