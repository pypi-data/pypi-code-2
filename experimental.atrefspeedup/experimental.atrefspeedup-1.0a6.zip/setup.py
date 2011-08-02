from setuptools import setup

version = '1.0a6'

setup(name='experimental.atrefspeedup',
      version=version,
      description="Speedup of the Archetypes reference engine.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone reference speed',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com/',
      license='GPL version 2',
      packages=['experimental', 'experimental.atrefspeedup'],
      namespace_packages=['experimental'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.testcaselayer',
          'Products.Archetypes',
          'Products.CMFCore',
          'Products.PloneTestCase',
          # 'Products.ZCatalog', Zope 2.13+
          'Zope2',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
