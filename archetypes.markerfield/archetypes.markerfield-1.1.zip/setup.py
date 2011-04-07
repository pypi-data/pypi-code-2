from setuptools import setup, find_packages

version = '1.1'

setup(name='archetypes.markerfield',
      version=version,
      description="Interface marker field for Archetypes",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Wichert Akkertman',
      author_email='wichert@wiggy.net',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['archetypes'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          'Products.Archetypes',
          'zope.interface',
      ],
      )
