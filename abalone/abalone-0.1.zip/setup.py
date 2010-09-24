#!/usr/bin/env python

from distutils.core import setup

setup(
        name='abalone',
        version='0.1',

        author='Unai Zalakain De Graeve',
        author_email='zalaka@gmail.com',
        url='http://lagunak.gisa-elkartea.org/projects/abalone',
        license='GPL v3',

        description='Abalone strategy game',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: X11 Applications',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Programming Language :: Python',
            'Topic :: Games/Entertainment :: Board Games',
            'Topic :: Games/Entertainment :: Turn Based Strategy',
            ],

        packages=['abalone'],
        package_data={'abalone': ['images/*']},
        scripts=['scripts/abalone'],
        requires=['Tkinter'],
        )
