from distutils.core import setup

setup(
   name="two2three",
   packages=['two2three','two2three.fixes','two2three.pgen2'],
   package_data={'two2three':['Grammar.txt','PatternGrammar.txt']},
   scripts=["2to3"],
   version="84300",
   author="python-dev",
   author_email="python-dev at python org",
   description="A copy of 2to3 from the sandbox",
   long_description="This is provided as a helper package for lib3to2, which depends on a particularly recent (at the time of writing) version of lib2to3.",
   maintainer="Joe Amenta",
   maintainer_email="amentajo at msu edu",
)
