# -*- encoding: utf-8
import sys
if sys.version_info[0] < 3:
    print("PySkein requires Python 3.0 or later!\n")
    sys.exit(1)


from distutils.core import setup, Extension


LONG_DESCRIPTION = ""
try:
    with open("doc_src/description.rst") as f:
        for line in f:
            if not line.startswith(".. "):
                for ch in ("`", "_", "**"):
                    line = line.replace(ch, "")
                LONG_DESCRIPTION += line
except IOError:
    pass

ext = Extension("_skein",
                sources=["src/threefish.c", "src/_skeinmodule.c"],
                include_dirs=["src"])

setup(name="pyskein",
      version="0.6.3",
      description="Implementation of the Skein hash function",
      long_description=LONG_DESCRIPTION,
      author="Hagen Fürstenau",
      author_email="hagen@zhuliguan.net",
      license="GPL",
      url="http://packages.python.org/pyskein/",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Information Technology",
          "Intended Audience :: Developers",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.0",
          "Programming Language :: Python :: 3.1",
          "Topic :: Security :: Cryptography"],
      package_dir={"": "src"},
      py_modules=["skein"],
      ext_modules=[ext],
      scripts=["scripts/skeinsum", "scripts/threefish"])
