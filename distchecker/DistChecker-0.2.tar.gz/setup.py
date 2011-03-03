import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()


setup(name='DistChecker',
      version='0.2',
      description=('Helper utiltiies for distutils such as '
                   'checking the sanity of an sdist'),
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://github.com/serverzen/DistChecker',
      keywords='distutils sdist',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      entry_points="""
        [console_scripts]
        distchecker=distchecker:main
      """
      )
