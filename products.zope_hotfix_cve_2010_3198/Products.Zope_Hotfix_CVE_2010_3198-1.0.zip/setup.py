from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='Products.Zope_Hotfix_CVE_2010_3198',
      version=version,
      description="Hotfix to fix CVE 2010-3198 for Zope < 2.10",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "License :: OSI Approved :: Zope Public License",
        ],
      keywords='security hotfix patch',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      url='http://svn.zope.org/Zope/hotfixes/Products.Zope_Hotfix_CVE_2010_3198',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      )
