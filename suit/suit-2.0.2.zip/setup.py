from setuptools import setup, find_packages
setup(
    name = 'suit',
    version = '2.0.2',
    packages = ['suit'],
    install_requires = ['docutils>=0.3'],
    author = 'Brandon Evans and Chris Santiago',
    author_email = 'admin@brandonevans.org and faltzermaster@aol.com',
    description = """SUIT Framework (Scripting Using Integrated Templates)
allows developers to define their own syntax for transforming templates by using rules.""",
    keywords = """template framework parser translator lightweight structure separation language independent clean syntax simple usage""",
    license = 'LGPL',
    url = 'http://www.suitframework.com/',
    zip_safe = False
)