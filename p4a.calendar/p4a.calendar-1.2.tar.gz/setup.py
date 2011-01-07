from setuptools import setup, find_packages
version = '1.2'

readme = open('README.txt')
long_description = readme.read()
readme.close()

setup(name='p4a.calendar',
      version=version,
      description="Plone4Artists calendar abstraction library",
      long_description=long_description,
      classifiers=[
          'Framework :: Zope3',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='Plone4Artists',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://pypi.python.org/pypi/p4a.calendar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.common>=1.0.1',
          'p4a.z2utils>=1.0',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
