from setuptools import setup, find_packages
import os

versionfile = open(os.path.join('collective', 'lastlogin', 'version.txt'))
version = versionfile.read().strip()
versionfile.close()


setup(name='collective.lastlogin',
      version=version,
      description="Show the list of Plone users with the last login date.",
      long_description=\
          open(os.path.join('collective', 'lastlogin', 'README.txt')).read() +
          '\n' +
          open(os.path.join('collective', 'lastlogin', 'HISTORY.txt')).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url='http://svn.plone.org/svn/collective/collective.lastlogin',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
