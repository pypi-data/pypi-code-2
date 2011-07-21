#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

# d2to1 basically installs itself!  See setup.cfg for the project metadata.
from d2to1.util import cfg_to_args

setup(
    use_2to3=True,
    zip_safe=False,
    entry_points={
        'distutils.setup_keywords': ['d2to1 = d2to1.core:d2to1'],
        'zest.releaser.prereleaser.middle':
            ['d2_version = d2to1.zestreleaser:prereleaser_middle'],
        'zest.releaser.postreleaser.middle':
            ['d2_version = d2to1.zestreleaser:postreleaser_middle']
    },
    **cfg_to_args()
)
