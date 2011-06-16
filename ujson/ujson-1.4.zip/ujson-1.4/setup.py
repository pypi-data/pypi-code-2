from distutils.core import setup, Extension
import distutils.sysconfig

module1 = Extension('ujson',
                    sources = ['ultrajsonenc.c', 'ultrajsondec.c', 'ujson.c', 'objToJSON.c', 'JSONtoObj.c'],
                    include_dirs = ['./'],
					library_dirs = [],
					libraries=[])
					
setup (name = 'ujson',
		version = '1.4',
		description = 'Ultra fast JSON encoder and decoder for Python',
		ext_modules = [module1],
		author = "Jonas Tarnstrom",
		author_email = "jonas.tarnstrom@esn.me",
		maintainer = "Jonas Tarnstrom",
		maintainer_email = "jonas.tarnstrom@esn.me",
		license = "BSD")

