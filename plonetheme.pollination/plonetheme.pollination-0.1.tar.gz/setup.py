from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='plonetheme.pollination',
      version=version,
      description="Pollination Theme",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='web zope plone theme diazo',
      author='Irene Capatti',
      author_email='irene.capatti@redturtle.it',
      url='http://svn.plone.org/svn/collective/plonetheme.pollination',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonetheme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.theming',
      ],
      entry_points={
          'z3c.autoinclude.plugin':'target = plone',
      },
)
