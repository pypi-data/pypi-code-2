from distutils.core import setup

setup(name="pyscripting",
      version="0.1",
      py_modules=["scripting"],
      description="Shell scripting library for Python",
      author="Mantas Zimnickas",
      author_email="sirexas@gmail.com",
      url="https://bitbucket.org/sirex/pyscripting/src",
      keywords=["shell", "scripting"],
      classifiers=[
          "Programming Language :: Python",
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU Library or Lesser General Public "
          "License (LGPL)",
          "Operating System :: Unix",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Utilities",
          ],
      long_description=open('README.rst').read())
