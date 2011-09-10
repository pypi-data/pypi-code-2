from setuptools import setup, find_packages

VERSION = '0.0.11'
try:
    README = open('README.rst').read()
except IOError:
    README = ''

setup(
    name     = 'zenpad',
    version  = VERSION,
    author   = 'Imbolc',
    author_email = 'imbolc@imbolc.name',
    description = 'Tree-structured notepad',
    long_description = README,
    zip_safe   = False,
    packages = find_packages(),
    include_package_data = True,
    url = 'http://zenpad.ru/',    
    entry_points = {
        'gui_scripts': [
            'zenpad = zenpad.zenpad:main',
        ]
    },
    install_requires=['markdown'],
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: Russian",
        "Topic :: Text Editors",
    ],
)
