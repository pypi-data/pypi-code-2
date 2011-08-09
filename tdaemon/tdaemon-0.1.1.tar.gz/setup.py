try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
setup(
    name = "tdaemon",
    version = "0.1.1",
    maintainer = "John Paulett",
    maintainer_email = "john@7oars.com",
    description = "Test Daemon",
    long_description = "The test daemon watches the content of files in a directory and if any of them changes (the content is edited), it runs the tests.",
    url = "http://github.com/brunobord/tdaemon",
    license = "MIT",
    platforms = ['POSIX', 'Windows'],
    keywords = ['test', 'testing', 'noestests', 'django', 'py.test'],
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
    ],    
    entry_points = {
      'console_scripts': [
        'tdaemon = tdaemon:main',
      ],
    },
    py_modules = ['tdaemon'],

)

