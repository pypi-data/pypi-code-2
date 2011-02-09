from distutils.core import setup
setup(
    name                = 'binstr',
    version             = '1.0',
    py_modules          = ['binstr'],
    description         = 'Utility functions for strings of binary digits',
    author              = 'David McEwan',
    author_email        = 'dmcewa15@caledonian.ac.uk',
    license             = 'GLPv3',
    platforms           = 'Python >2.6 including 3.x (OS Independent)',
    
    classifiers         = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 5 - Production/Stable'
                          ],
    
    long_description    = '''
Binstr - A collection of utility functions for creating and operating on
         strings of binary digits. It is compatible with Python versions >2.6
         including 3.x.
         It is useful to use these functions to make small bugs in your code
         easier to find since all inputs are checked thoroughly for errors
         using assertions.

Includes:
int_to_b()  - Convert a positive integer to a sting of binary
              e.g. int_to_b(5) -> '00000101'
frac_to_b() - Convert a positive fraction to a string of binary
              e.g. frac_to_b(0.5) -> '10000000'

b_and()  - Perform a bitwise AND
b_or()   - Perform a bitwise OR
b_xor()  - Perform a bitwise XOR
b_nand() - Perform a bitwise NAND
b_nor()  - Perform a bitwise NOR
b_nxor() - Perform a bitwise NXOR
b_not()  - Perform a bitwise NOT (inversion)

b_add()  - Perform an ADD operation
b_mul()  - Perform a MUL operation (multiply)
                          '''.rstrip()
     )
