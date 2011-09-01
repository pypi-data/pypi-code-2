from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='pdfserenitynow',
    version=version,
    description="Create TIFs and JPGs from crappy PDFs",
    long_description=README + '\n\n' + NEWS,
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Environment :: Console',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Natural Language :: English',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3',
                 'Topic :: Multimedia :: Graphics :: Graphics Conversion',
                 'Topic :: Printing',
                 'Topic :: Utilities'
    ],
    keywords='pdf print converter tiff jpg',
    author='Ben Rousch',
    author_email='brousch@gmail.com',
    url='',
    license='GPL',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['serenifypdf=pdfserenitynow.serenifypdf:main']
    }
)
