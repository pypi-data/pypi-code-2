from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(
  name = "MieLib1",
  version='1.0',
  description='Tool for mie factors for spherical perticles calculation',
  author='Konstantin Alrxandrovich Shmirko',
  author_email='shmirko.konstantin@gmail.com',
  license='GPL',
  ext_modules=[ 
    Extension("MieLib", ["MieLib.pyx","mie.c","complex.c", "array.c", "bracketroot.c", "legendre.c", "lobatto.c", "saferoot.c"],
	depends=["mie.h"],
	include_dirs=['.'],
	libraries=['m'])
    ],
  cmdclass = {'build_ext': build_ext}
)
