from distutils.core import setup, Extension

setup(name="watcher",
      version="0.2",
      description="FileSystemWatcher clone for CPython",
      keywords="watcher, FileSystemWatcher",
      maintainer="Brian Curtin",
      maintainer_email="brian@python.org",
      license="PSF",
      platforms=["Win"],
      py_modules=["FileSystemWatcher"],
      packages = ["watcher", "watcher.tests"],
      ext_modules=[Extension("watcher._watcher", ["src/_watcher.c"],
                            # Compile with higher warning level
                            # Define UNICODE since this was developed
                            # with wide strings in mind, aka.
                            # "Use Unicode Character Set" was enabled
                            # in Visual Studio.
                             extra_compile_args=["/W4", "/DUNICODE"])],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Python Software Foundation License",
          "Operating System :: Microsoft",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: Microsoft :: Windows :: Windows NT/2000",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.1",
          "Programming Language :: Python :: 3.2",
          "Topic :: System :: Filesystems"],
      long_description=open("README.txt").read()
      )


