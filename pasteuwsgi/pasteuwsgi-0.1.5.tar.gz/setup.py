from setuptools import setup

import pasteuwsgi

setup(
    name='pasteuwsgi',
    version=pasteuwsgi.__version__,
    author=pasteuwsgi.__author__,
    author_email=pasteuwsgi.__email__,
    packages=['pasteuwsgi'],
    include_package_data = True,
    url='http://pypi.python.org/pypi/pasteuwsgi/',
    license='LICENSE.txt',
    description='Paster command to use uwsgi as server for local development',
    long_description=open('README').read(),
    install_requires = [
        "PasteScript>=1.3",
        "pyinotify"
    ],
    test_suite = 'nose.collector',
    tests_require = [ "Nose" ],
    classifiers  = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Terminals",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Framework :: Paste"
    ],
    entry_points = """
    [paste.paster_command]
    uwsgi = pasteuwsgi.serve:ServeCommand
    """
)
