from distutils.core import setup
from glob import glob
import os

long_desc="""
Composite is a metaclass implementing composition instead of multiple inheritance.  Inspired by Michele Simionato's straits package. (Thanks, Michele!)

Composite sources (aka Parts) are a bunch of methods and attributes with the following properties:

   1. the methods/attributes in a Part belong logically together
   2. if a Part enhances a class, then all subclasses are enhanced too
   3. if a Part has methods in common with the class, then the methods defined in the class have precedence
   4. the Parts order is not important, i.e. enhancing a class first with Part P1 and then with Part P2 or viceversa is the same
   5. if parts P1 and P2 have names in common, enhancing a class with P1 and P2 raises an error
          because the final class has final say, conflicts can be resolved there (by hand)
   6. if a Part has methods in common with the base class, then the Part methods have precedence
   7. a class can be seen both as a composition of Parts and as an homogeneous entity
"""

setup( name='composite',
       version='0.03.000',
       license='BSD License',
       description='Metaclass implementing composition instead of multiple inheritance',
       long_description=long_desc,
       url='',
       packages=['composite'],
       provides=['composite'],
       author='Ethan Furman',
       author_email='ethan@stoneleaf.us',
       classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development' ],
     )

