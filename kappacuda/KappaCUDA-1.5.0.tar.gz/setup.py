#!/usr/bin/env python

"""
setup.py file for SWIG KappaCUDA
"""

from distutils.core import setup, Extension

KappaCUDA_module = Extension('_KappaCUDA',
      sources=['KappaCUDA_wrap.cpp'],
      define_macros=[('USE_OPENGL','1')],
      include_dirs=['/usr/local/cuda/include', '/Program Files/Kappa/include'],
      library_dirs=['/Program Files/Kappa/lib'],
      libraries=['Kappa', 'KappaConfig', 'KappaParser', 'KappaPlugin', 'ffi', 'pcrecpp', 'cuda'],
                           )

setup (name = 'KappaCUDA',
       version = '1.5.0',
       author      = 'Psi Lambda LLC',
       author_email='kappa@psilambda.com',
       url='http://psilambda.com',
       description = """Module to give easy access to NVIDIA CUDA from Python using the Kappa Library.""",
       ext_modules = [KappaCUDA_module],
       py_modules = ["KappaCUDA"],
       )
