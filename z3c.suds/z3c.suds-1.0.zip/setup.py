from setuptools import setup, find_packages

version = '1.0'

setup(name='z3c.suds',
      version=version,
      description="Manages a pool of suds SOAP clients within the context of a Zope application",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='suds soap zope zodb',
      author='David Glick, Groundwire',
      author_email='davidglick@groundwire.org',
      url='http://svn.zope.org/z3c.suds/trunk',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'suds',
          # -*- Extra requirements: -*-
      ],
      )
