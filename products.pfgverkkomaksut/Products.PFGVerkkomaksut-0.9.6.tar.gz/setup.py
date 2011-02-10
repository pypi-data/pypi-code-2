from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('Products', 'PFGVerkkomaksut', 'version.txt')[:-1]

long_description = (
    open("README.txt").read() + "\n" +
    open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
    open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
    open(os.path.join("docs", "CREDITS.txt")).read()
    )

setup(name='Products.PFGVerkkomaksut',
      version=version,
      description="Products.PFGVerkkomaksut provides verkkomaksut payment adapter to Products.PloneFormGen package.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Taito Horiuchi',
      author_email='taito.horiuchi@gmail.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PloneFormGen',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
