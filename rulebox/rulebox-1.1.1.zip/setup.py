from setuptools import setup, find_packages
setup(
    name = 'rulebox',
    version = '1.1.1',
    packages = ['rulebox'],
    install_requires = ['docutils>=0.3'],
    author = 'Brandon Evans and Chris Santiago',
    author_email = 'admin@brandonevans.org and faltzermaster@aol.com',
    description = """A package containing various sets of rules for use with
    SUIT.""",
    keywords = """suit template rules rulesets""",
    license = 'LGPL',
    url = 'http://www.suitframework.com/',
    zip_safe = False
)