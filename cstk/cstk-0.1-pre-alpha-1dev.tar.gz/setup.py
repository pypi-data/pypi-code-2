from setuptools import setup, find_packages
import sys, os

# Dynamically calculate the version based on cstk.VERSION.
version = __import__( 'cstk' ).get_version()
if u'SVN' in version:
    version = ' '.join( version.split( ' ' )[:-1] )

readme_file_contents = ''

try:
    readme_file = open( 'README', 'r' )
    readme_file_contents = readme_file.read()
    readme_file.close()
except IOError:
    pass

setup( 
    name="cstk",
    version=version.replace( ' ', '-' ),
    url='http://www.irondev.org/',
    author='Paul O\'Connor',
    author_email='p@p-ocon.com',
    maintainer='Paul O\'Connor',
    maintainer_email='p@p-ocon.com',
    description="A set of apps for the Django Framework that does the gruntwork for you.",
    long_description=readme_file_contents,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='django localisation translation',
    license='GPL',
    packages=find_packages( exclude=['ez_setup', 'examples', 'tests'] ),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
 )
