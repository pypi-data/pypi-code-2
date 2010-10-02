from distutils.core import setup

setup(
    name = "my_xml",
    version = "0.1.0",
    py_modules=["my_xml"],

    # metadata for uploading to PyPI
    author = "Erez Bibi",
    author_email = "erezbibi@users.sourceforge.net",
    description = "Very simple and easy to use XML parser",
    keywords = "Simple XML Parser",
    long_description = """
Help module to parse a simple XML buffer and store it as a read-only (mostly)
dictionary type object (MyXml). This dictionary can hold other dictionaries,
nodes-lists, or leaf nodes. Access to the nodes by using attributes.

>>> xml = parse("<Foo><Bar>Val</Bar></Foo>")
>>> xml.Foo.Bar == "Val"
True

I don't like to use the built in Python DOM parsers for simple XML data, but
this module is good only for simple XML! No name-spaces, CDATA and other fancy
features are supported.

There are three factory functions, "parse", "parse_file" and "parse_object".

- parse takes an XML string and builds MyXml object from it.

- parse_file takes a file name reads it and do the same.

- parse_object takes a complex python object (of dictionaries, sequences and
scalars) and creates MyXml object from it.

It is possible, but not convenient, to construct an XML trees using this module.

see my_xml built in documentation for usage examples.
""",
    classifiers = [
    'Intended Audience :: Developers',
    'License :: Public Domain',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Text Processing :: Markup :: XML',
    'Topic :: Utilities'
    ]
)
