#!/usr/bin/env python

#
# epubmaker setup
#

from setuptools import setup
# from distutils.core import setup

from epubmaker.Version import VERSION

# NOTE: bdist_wininst doesn't install dependencies by design

setup (
    name = "epubmaker",
    version = VERSION,

    install_requires = [
        'setuptools',
        'docutils >= 0.7',
        'lxml >= 2.2.8',
        'cssutils >= 0.9.7',
        'PIL >= 1.1.7',
        # 'uTidylib >= 0.2',
       ],
    
    zip_safe = True,

    requires = [
        'setuptools',             # actually pkg_resources
        'docutils (>= 0.7)',
        'lxml (>= 2.2.8)',
        'cssutils (>= 0.9.7)',
        'PIL (>= 1.1.7)',
        # 'uTidylib (>= 0.2)',
        ],

    packages = [
        'epubmaker',
        'epubmaker.lib',
        'epubmaker.parsers',
        'epubmaker.writers',
        'epubmaker.packagers',
        'epubmaker.mydocutils',
        'epubmaker.mydocutils.writers',
        'epubmaker.mydocutils.transforms',
        'epubmaker.mydocutils.parsers',
        ],
    
    # you have to put these files both here *and* in MANIFEST.in !!!
    data_files = [
        ('epubmaker/parsers', ['epubmaker/parsers/broken.png',
                               'epubmaker/parsers/pg-license.rst']),
        ('epubmaker/writers', ['epubmaker/writers/rst2all.css',
                               'epubmaker/writers/rst2html.css',
                               'epubmaker/writers/rst2epub.css',
                               'epubmaker/writers/cover.jpg']),
        ],

    entry_points = {
          'console_scripts':
              ['epubmaker = epubmaker.EpubMaker:main']
        },

    # metadata for upload to PyPI
    
    author = "Marcello Perathoner",
    author_email = "webmaster@gutenberg.org",
    description = "The Project Gutenberg Epub Maker",
    long_description = "The tool used internally at Project Gutenberg to convert HTML or plain text ebooks to EPUBs. Can also process reST into EPUB.",
    license = "GPL v3",
    keywords = "epub rst reST reStructuredText gutenberg ebook conversion",
    url = "http://pypi.python.org/pypi/epubmaker/",
    # download_url = "http://www.gutenberg.org/tools/",

    classifiers = ["Topic :: Text Processing",
                   "License :: OSI Approved :: GNU General Public License (GPL)",
                   "Environment :: Console",
                   "Operating System :: OS Independent",
                   "Intended Audience :: Other Audience",
                   "Development Status :: 4 - Beta"],
                   
    platforms = 'OS-independent',
)
