from setuptools import setup, find_packages

version = '1.1'

setup(name='Products.PloneHotfix20110720',
      version=version,
      description="Plone security hotfix addressing CVE 2011-0720",
      long_description=open("README.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Zope2",
        ],
      keywords='security hotfix patch',
      author='Plone security team',
      author_email='security@plone.org',
      url='http://plone.org/products/plone/security/advisories/cve-2011-0720',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      )
