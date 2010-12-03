import os
import sys

from setuptools import setup, find_packages

execfile(os.path.join("tw", "rum", "release.py"))

setup(
    name=__DISTRIBUTION__,
    version=__VERSION__,
    description=__DESCRIPTION__,
    author=__AUTHOR__,
    author_email=__EMAIL__,
    url=__URL__,
    install_requires=[
        'tw.forms >= 0.9.2',
        'ToscaWidgets >= 0.9.4dev_20080829, ==dev',
        'rum >= 0.3dev-20090708',
        'tw.dojo >=0.8',
        'python-dateutil',
        ],
    extras_require = {
        'tinymce': ['tw.tinymce'],
    },
    packages=find_packages(exclude=['ez_setup', 'tests']),
    namespace_packages = ['tw'],
    zip_safe=False,
    include_package_data=True,
    test_suite = 'nose.collector',
    entry_points="""
    [toscawidgets.widgets]
    # Register your widgets so they can be listed in the WidgetBrowser
    widgets = tw.rum
    samples = tw.rum.samples

    [rum.viewfactory]
    toscawidgets = tw.rum:WidgetFactory
    """,
    message_extractors = {'tw/rum': [
        ('**.py', 'python', None),
        ('**.html', 'genshi', {'extract_text':False}),
        ]},
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
