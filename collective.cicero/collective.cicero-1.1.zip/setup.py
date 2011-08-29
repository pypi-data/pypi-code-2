from setuptools import setup, find_packages

version = '1.1'

setup(name='collective.cicero',
      version=version,
      description="Provides access to Azavea's Cicero API for legistrative district matching and elected official info",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='azavea cicero legislative lookup elected official soap zope plone',
      author='David Glick, Groundwire',
      author_email='davidglick@groundwire.org',
      url='http://svn.plone.org/svn/collective/collective.cicero/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'plone.registry',
          'plone.app.registry',
          'setuptools',
          'z3c.form',
          'z3c.suds',
          'zope.component',
          'zope.dottedname', # undeclared dep of plone.registry
          'zope.interface',
          'zope.schema',
          # -*- Extra requirements: -*-
      ],
      )
