from setuptools import setup, find_packages

version = '0.8'

setup(name='zope.z2release',
      version=version,
      description="Zope release helper",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Zope Foundation',
      author_email='zope-dev@zope.org',
      url='http://pypi.python.org/pypi/zope.z2release',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zope'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points=dict(console_scripts=[
        'z2_kgs=zope.z2release.cli:main',
        'ztk_kgs=zope.z2release.ztk:main'
        ]),
      )
