from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1.1dev'

install_requires = [
    "mechanize",
    "nose",     #TODO: this should be made optional for end-users
    "openmeta", #TODO: this should be made optional
]


setup(name='citeulike_api',
    version=version,
    description="a python api for http://citeulike.org/",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Topic :: Internet :: WWW/HTTP :: Browsers',
    ],
    keywords='',
    author='Dan MacKinlay',
    author_email='pypi@email.possumpalace.org',
    url='https://bitbucket.org/howthebodyworks/citeulike_api/src',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
