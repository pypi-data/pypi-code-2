from distutils.core import setup
from Pyrex.Distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(name='pappy',
	version='0.91',
	ext_modules=[									\
		Extension(									\
			'pappy',								\
			['pappy.pyx'],							\
			libraries=['portaudio'],				\
		)],
	cmdclass = {'build_ext': build_ext},			\
	description='Python Distribution Utilities',	\
	author='Dale Cieslak',							\
	author_email='desizzle@users.sourceforge.net',	\
	url='http://pappy.sourceforge.net/',			\
	classifiers = [
        	"Programming Language :: Python",
        	"Development Status :: 4 - Beta",
        	"Intended Audience :: Developers",
        	"Operating System :: OS Independent",
        	"Topic :: Multimedia :: Sound/Audio",
	],

)


