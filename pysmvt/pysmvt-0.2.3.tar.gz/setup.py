"""
Pysmvt has been replaced by BlazeWeb and family.

The `pysmvt tip <http://bitbucket.org/rsyring/pysmvt/get/tip.zip#egg=pysmvt-dev>`_
is installable via `easy_install` with ``easy_install pysmvt==dev``
"""
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.2.3'

setup(
    name = "pysmvt",
    version = version,
    description = "A wsgi web framework with a pylons spirit and django modularity",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://pypi.python.org/pypi/pysmvt/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    install_requires = [
        "Beaker>=1.5",
        "decorator>=3.0.1", ## <-- is used?
        "FormEncode>=1.2",
        "html2text>=2.35",
        "jinja2>=2.5",
        "markdown2>=1.0.1",
        "minimock>=1.2",
        "nose>=0.11",
        "Paste>=1.7",
        "PasteScript>=1.7",
        "pysutils>=0.2",
        "simplejson>=2.0", #but only on 2.5, and only if using the json wrapper
        "WebHelpers>=1.0rc1",
        "Werkzeug>=0.6"
    ],
    entry_points="""
    [console_scripts]
    pysmvt = pysmvt.script:main

    [pysmvt.pysmvt_project_template]
    pysmvt = pysmvt.paster_tpl:ProjectTemplate

    [pysmvt.pysmvt_module_template]
    pysmvt = pysmvt.paster_tpl:ModuleTemplate

    [nose.plugins]
    pysmvt_initcurrentapp = pysmvt.test:InitCurrentAppPlugin
    """,
    zip_safe=False
)
