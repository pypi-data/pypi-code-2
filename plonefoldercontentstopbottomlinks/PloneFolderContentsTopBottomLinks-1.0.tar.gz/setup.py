from setuptools import setup, find_packages

version = '1.0'

setup(name='PloneFolderContentsTopBottomLinks',
      version=version,
      description="Patch folder contents to show top and bottom links (for Plone 3.x)",
      long_description=open("README.txt").read() + "\n\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
          "Framework :: Plone",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
      ],
      keywords='plone content views viewlet',
      author='Laurence Rowe',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/PloneFolderContentsTopBottomLinks',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.app.content',
      ],
      )
