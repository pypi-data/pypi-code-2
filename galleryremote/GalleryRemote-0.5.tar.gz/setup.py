from setuptools import setup, find_packages
import sys, os

version = '0.5'

setup(name='GalleryRemote',
      version=version,
      description="Implementation of the Gallery Remote protocol in Python.",
      long_description="""\
Implementation of the Gallery Remote protocol in Python.""",
      classifiers=['Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Multimedia :: Graphics'],
      keywords='gallery gallery2 remote images pictures albums',
      author='Pietro Battiston',
      author_email='me@pietrobattiston.it',
      url='http://code.google.com/p/galleryremote',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False
      )
