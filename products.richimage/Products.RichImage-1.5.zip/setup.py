from setuptools import setup, find_packages

version = '1.5'

long_description = (
    open('README.txt').read() + '\n' +
    open('CHANGES.txt').read()
    )

tests_require=['zope.testing']

setup(name='Products.RichImage',
      version=version,
      description="Image with crop functionalities.",
      long_description=long_description,
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.app.blob',
        ],
      )
