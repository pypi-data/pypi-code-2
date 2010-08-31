from setuptools import setup, find_packages
import sys, os

here    = os.path.abspath(os.path.dirname(__file__))
README  = open(os.path.join(here, 'README.rst')).read()
NEWS    = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1.1'

install_requires = [
    "baker>=1.1",
    "mutagen>=1.20",
    "odict>=1.3",
    'texttable >= 0.7.0',
]


setup(
    name                    = 'bp.tagging',
    version                 = version,
    description             = "Multimedia file tagging library",
    long_description        = README + '\n\n' + NEWS,
    classifiers             = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Utilities",
    ],
    keywords                = 'mp3 mp4 id3',
    author                  = 'Andreas Kaiser',
    author_email            = 'disko@binary-punks.com',
    url                     = 'http://github.com/disko/bp.tagging',
    license                 = 'BSD',
    packages                = find_packages('src'),
    package_dir             = {'': 'src'},
    namespace_packages      = ['bp'],
    include_package_data    = True,
    zip_safe                = False,
    install_requires        = install_requires,
    entry_points            = {
        'console_scripts':
            ['bp_tagging=bp.tagging:main']
    }
)
