from setuptools import setup, find_packages
version = '0.1'
name = "slapos.zcbworkarounds"

setup(
  name=name,
  version=version,
  description="A zc.buildout extensions to workaround zc.buildout issues"\
      " which are impacting ERP5 Appliance",
  long_description=open("README.txt").read() + "\n\n" +
    open("CHANGES.txt").read(),
  classifiers=[
      "Programming Language :: Python",
      "Framework :: Buildout :: Extension",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
  packages=find_packages(),
  entry_points={
     'zc.buildout.extension': ['extension = slapos.zcbworkarounds:extension'],
     },
  zip_safe=True,
  license='GPLv3',
)
