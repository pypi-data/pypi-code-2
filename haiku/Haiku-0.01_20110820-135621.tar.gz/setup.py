import os
# don't hard link! some systems attempt to hard link and fail
# (AFS, cygwin, maybe others)
del os.link
from distutils.core import setup, Extension
setup(name='Haiku',
	version='0.01',
	packages=[],
	ext_modules=[
		Extension(
			'Haiku',
			['Haiku.cc'],
#			extra_compile_args=["-Wno-multichar"]
# I don't like doing this, because the uninitialized warning is often useful,
# but I get too many false positives if I don't
			extra_compile_args=["-Wno-multichar", "-Wno-uninitialized"],
			runtime_library_dirs=["libbe", "libtracker"]
			)

		],
	)
