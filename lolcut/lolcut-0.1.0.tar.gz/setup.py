import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "lolcut",
    version = "0.1.0",
    platforms = "all",
    
    packages = find_packages(),
    
    install_requires = ['mutagen', 'chardet'],
    
    package_data = {
        '': ['README', 'TODO'],
    },
    
    entry_points = {
        'console_scripts' : [
            'lolcut = lolcut.main:main'
        ],
    },
    
    author = "Dmitry Soldatov",
    author_email = "grapescan@gmail.com",
    url = "https://bitbucket.org/boh/lolcut",
    download_url = "https://bitbucket.org/boh/lolcut/downloads/lolcut-0.1.0.tar.gz",
    license = "GPL",
    keywords = "shntool loseless image cue sheet split flac ape wv tag",
    description = "Splits loseless images into tracks, renames tracks, sets tags",
    long_description = """
    Splitting tool for loseless music. Splits image(APE, FLAC, WV, etc) into single FLAC tracks according to CUE sheet.
    Has recursive search for CUE files under selected directory (usefull for huge collections).
    Renames resulting files and sets metadata (tags) according to CUE sheet.
    """,
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers for
    # full list of available classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
    ],    
) 
