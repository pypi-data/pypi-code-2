import os
import sys
from setuptools import setup, find_packages

setup(
    name="abl.jquery.ui",
    version="1.8.7-3",
    description="UI-Extensions for jQuery",
    author="Diez B. Roggisch",
    author_email="deets@web.de",
    url="http://bitbucket.org/deets/abljqueryui",
    license="MIT",
    download_url='http://bitbucket.org/deets/abljqueryui/downloads/',
    install_requires=[
        "abl.util>=0.1",
        "abl.jquery>=1.4",
        "abl.jquery.plugins.form>=2.28"
        ],
    packages=find_packages(exclude=['ez_setup', 'tests']),
    package_data = {'': ['*.html', '*.txt', '*.rst']},
    namespace_packages = ['abl', 'abl.jquery', 'abl.jquery', 'abl.jquery.examples'],
    zip_safe=False,
    include_package_data=True,
    test_suite = 'nose.collector',
    entry_points="""
    [toscawidgets.widgets]
    widgets = abl.jquery.plugins.ui
    """,
    keywords = [
        'toscawidgets.widgets',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
