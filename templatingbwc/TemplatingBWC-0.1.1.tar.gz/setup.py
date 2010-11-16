"""
Introduction
---------------

TemplatingBWC is a component for `BlazeWeb <http://pypi.python.org/pypi/BlazeWeb/>`_
applications.  Its main purpose is to provide a customizable yet generic
template appropriate for back-end, control-panel, or similiar use-oriented web
applications.

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

Current Status
---------------

The code stays pretty stable, but the API may change in the future.

The `TemplatingBWC tip <http://bitbucket.org/rsyring/templatingbwc/get/tip.zip#egg=templatingbwc-dev>`_
is installable via `easy_install` with ``easy_install TemplatingBWC==dev``.
"""

from setuptools import setup, find_packages

import templatingbwc
version = templatingbwc.VERSION

setup(
    name = "TemplatingBWC",
    version = version,
    description = "A BlazeWeb component with template themes",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://bitbucket.org/rsyring/templatingbwc/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    packages=find_packages(exclude=['templatingbwc_*']),
    include_package_data = True,
    install_requires = [
        'BlazeForm>=0.3.0',
        'BlazeWeb>=0.3.0',
    ],
    zip_safe=False
)
