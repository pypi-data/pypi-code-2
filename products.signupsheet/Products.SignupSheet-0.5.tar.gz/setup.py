import os
from setuptools import setup, find_packages

CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Zope2',
    'Framework :: Plone',
]

version_file = os.path.join('Products', 'SignupSheet', 'version.txt')
version = file(version_file).read().strip()
desc = file('README.txt').read().strip()
changes = file('CHANGES.txt').read().strip()

long_description = desc + '\n\nCHANGES\n=======\n\n' +  changes 

setup(name='Products.SignupSheet',
      version=version,
      license='GPL2',
      author='Aaron VanDerlip and others',
      author_email='avanderlip@gmail.com',
      maintainer='Aaron VanDerlip',
      maintainer_email='avanderlip@gmail.com',
      classifiers=CLASSIFIERS,
      keywords='Archetypes Plone Zope Python', 
      url='http://pypi.python.org/pypi/Products.SignupSheet',
      description='A signup sheet implementation for Plone',
      long_description=long_description,
      packages=['Products', 'Products.SignupSheet'],
      install_requires=('setuptools',
                        'Products.ATSchemaEditorNG', 
                        'Products.TALESField', 
                        'Products.TemplateFields'),
      include_package_data = True,
      zip_safe=False,
      namespace_packages=['Products'],

      )
