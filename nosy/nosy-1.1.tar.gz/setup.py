from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

djl_url = "http://douglatornell.ca/software/python/nosy/"
nosy_version = "1.1"
version_classifiers = ['Programming Language :: Python :: %s' % version
                       for version in ['2', '2.5', '2.6', '2.7']]
other_classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: BSD License',
    'Intended Audience :: Developers',
    'Environment :: Console',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Testing',
    ]

readme_file = open('README', 'rt')
try:
    detailed_description = readme_file.read()
finally:
    readme_file.close()

setup(
    name="nosy",
    version=nosy_version,
    description="""\
Run the nose test discovery and execution tool whenever a source file
is changed.
    """,
    long_description=detailed_description,
    author="Doug Latornell",
    author_email="djl@douglatornell.ca",
    url=djl_url,
    download_url="%(djl_url)snosy-%(nosy_version)s.tar.gz" % locals(),
    license="New BSD License",
    classifiers=version_classifiers + other_classifiers,
    packages=find_packages(),
    entry_points={'console_scripts':['nosy = nosy.nosy:main']}
)
