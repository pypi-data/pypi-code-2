from setuptools import setup, find_packages
import sys, os

# So we can import handcrank
sys.path.append('./src')

from handcrank import version

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.rst')).read()

install_requires = [
    'docutils>=0.7',
    'Jinja2==2.5.2',
    'Pygments>=0.8',
]

pyversion = sys.version_info
if pyversion[0] == 2 and pyversion[1] < 7:
    # We need to include argparse, it's not part of the standard lib
    install_requires.append('argparse>=1.1')
    install_requires.append('ordereddict>=1.1')
    install_requires.append('unittest2>=0.5.1')

setup(name='handcrank',
    version=version.number,
    description="A very simple static site generator using reStructuredText",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='rst restructuredtext site generator',
    author='Rob Madole',
    author_email='robmadole@gmail.com',
    url='http://github.com/robmadole/handcrank',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['handcrank=handcrank:main']
    }
)
