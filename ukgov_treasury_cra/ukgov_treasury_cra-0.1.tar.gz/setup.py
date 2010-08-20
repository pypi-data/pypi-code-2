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
    name='ukgov_treasury_cra',
    version=version,
    description="HM Treasury's Country and Regional Analysis",
    long_description="""\
HM Treasury's Country and Regional Analysis""",
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
    keywords="cra uk",
    author='Open Knowledge Foundation',
    author_email='okfn-help@lists.okfn.org',
    url="http://purl.org/okfn/dataset/cra/2009",
    license='AGPL',
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
        "unstats_rdf",
        "eurostat_rdf",
    ],
    datapkg_index = """
        [cra2009]
        id=9e512b59-ef2d-445b-a728-5125208bed4a
        title=Country and Regional Analysis 2009 - CSV
        download_url=http://www.hm-treasury.gov.uk/d/cra_2009_db.csv
        license=OKD Compliant::UK Crown Copyright with data.gov.uk rights
        author=HM Treasury
        maintainer=Where Does My Money Go
        url=http://www.hm-treasury.gov.uk/pesp_cra.htm
    """,
    entry_points = """
        [console_scripts]
        cra2009=ukgov.hmt.cra:cra2009
    """,
)
