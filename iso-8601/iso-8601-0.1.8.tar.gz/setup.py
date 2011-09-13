from distutils.core import setup
import iso8601

setup(
    name = "iso-8601",
    version = iso8601.__version__,
    description = "Flexible ISO 8601 parser: pass in a valid ISO 8601 string, or a date(time) object and a datetime object will be returned.",
    url = "http://hg.schinckel.net/iso-8601/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "iso8601",
    ],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
    ],
)
