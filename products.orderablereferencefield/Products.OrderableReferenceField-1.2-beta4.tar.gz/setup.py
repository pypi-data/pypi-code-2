import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2-beta4'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
#    + '\n' +
#    read('Products', 'OrderableReferenceField', 'README.txt')
#    + '\n' +
#    read('CONTRIBUTORS.txt')
    )

setup(name='Products.OrderableReferenceField',
      version=version,
      description="This product provides an Archetype field that's very similiar \
        to the Archetypes Reference field, with the addition that it stores the \
        order of referenced objects",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Daniel Nouri',
      author_email='daniel.nouri@gmail.com',
      url='http://svn.plone.org/svn/archetypes/Products.OrderableReferenceField/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
