from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='ulif.pynotify',
      version=version,
      description="Helpers to bridge different Python envs and OpenOffice.org.",
      long_description=open("README.txt").read() + "\n\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Buildout",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='filesystem changes monitor watchdog inotify',
      author='Uli Fouquet',
      author_email='uli at gnufix.de',
      url='http://pypi.python.org/pypi/ulif.pynotify',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir = {'': 'src'},
      namespace_packages=['ulif', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zc.buildout',
      ],
      setup_requires=["Sphinx-PyPI-upload"],
      extras_require=dict(
        test = [
            'zope.testing',
            'zc.recipe.egg',
            ],
        docs = [
            'Sphinx',
            'collective.recipe.sphinxbuilder',
            'docutils',
            'roman',
            ],
        sqlite = [
            'pysqlite',
            ],
        ),
      entry_points="""
      [console_scripts]
      pynotify-ctl = ulif.pynotify.ui.pynotifyctl:main
      pynotify = ulif.pynotify.ui.pynotify:main
      """,
      )
