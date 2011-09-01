from setuptools import setup, find_packages

version = '1.3'

setup(name='Products.PloneFlashUpload',
      version=version,
      description="Add-on that allows mass-upload of files and images.",
      long_description=(
        open('README.txt').read() + '\n\n' + open('CHANGES.txt').read()
        ),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone upload images',
      author='Rocky Burt (3.0 support by Reinout van Rees)',
      author_email='reinout@zestsoftware.nl',
      url='http://plone.org/products/ploneflashupload',
      license='Zope Public License (ZPL) Version 2.1',
      package_dir={'':'src'},
      packages=find_packages('src'),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.i18n',
          'z3c.widgets.flashupload',
      ],
      )
