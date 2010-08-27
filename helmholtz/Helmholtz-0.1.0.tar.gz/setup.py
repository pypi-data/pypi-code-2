#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "Helmholtz",
    version = "0.1.0",
    packages = ['helmholtz', 'helmholtz.access_control', 'helmholtz.annotation',
                'helmholtz.chemistry', 'helmholtz.core',
                'helmholtz.drug_applications', 'helmholtz.electrophysiology',
                'helmholtz.equipment', 'helmholtz.experiment', 'helmholtz.location',
                'helmholtz.measurements', 'helmholtz.neuralstructures',
                'helmholtz.people', 'helmholtz.preparations', 'helmholtz.recording',
                'helmholtz.signals', 'helmholtz.species', 'helmholtz.stimulation',
                'helmholtz.storage', 'helmholtz.units'],
    package_data = {'helmholtz': ['people/fixtures/*.json', 'templates/*.html',
                                  'media/css/helmholtz.css']},
    author = "Neuroinformatics research group, UNIC, CNRS",
    author_email = "neuroinformatique@unic.cnrs-gif.fr",
    description = "A framework for creating neuroscience databases",
    #long_description = """LONG DESCRIPTION GOES HERE""",
    license = "CeCILL http://www.cecill.info",
    keywords = "neuroscience database Django metadata",
    url = "http://www.dbunic.cnrs-gif.fr/helmholtz/",
    classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Science/Research',
                   'License :: Other/Proprietary License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Framework :: Django',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Database'],
)

