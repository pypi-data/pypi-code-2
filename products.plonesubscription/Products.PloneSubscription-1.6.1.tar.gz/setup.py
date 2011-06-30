from setuptools import setup, find_packages
import os

def read(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = read('Products', 'PloneSubscription', 'version.txt')

setup(name='Products.PloneSubscription',
      version=version,
      description="A Plone tool supporting different levels of subscription and notification.",
      long_description=(read('Products', 'PloneSubscription', 'README.txt')
                        + '\n\n'
                        + read('Products', 'PloneSubscription', 'CHANGES')),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Plone"
          ],
      keywords='plone subscription',
      author='Alter Way Solutions',
      author_email='support@alterway.fr',
      url='http://svn.plone.org/svn/collective/Products.PloneSubscription',
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
      """,
      )
