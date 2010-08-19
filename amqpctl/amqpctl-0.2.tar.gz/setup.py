from setuptools import setup, find_packages
import sys, os

version = '0.2'
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

setup(name='amqpctl',
      version=version,
      description="AMQP Control Command Line Utility",
      long_description="""\
AMQP Control Command Line Utility""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='amqp',
      author='William Waites',
      author_email='ww@styx.org',
      url='http://packages.python.org/amqpctl',
      license='GPL',
      packages=["amqpctl"],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "amqplib",
      ],
      entry_points="""
        [console_scripts]
        amqpctl=amqpctl.command:amqpctl
      """,
      )
