from distutils.core import setup

setup(name='PyShada',
      version='0.9.0',
      packages=['shada'],
      author='Thinker K.F. Li',
      author_email='thinker@branda.to',
      url='http://www.assembla.com/spaces/pyshada/',
      description='Shell adaptor for Python',
      long_description='''
PYthon SHell ADApter to simplify calling shell commands from Python
code.  Calling shell commands is usually tedious, especially transfer
data between Python and shell domain. Creating a pipeline to call
several external tools in Python code is not as simple as shell
command doing. It is also hard to passing variables between domains,
you need tediously string joining/formatting and parsing.  PyShada
tries to help you for calling shell commands.
      ''',
      classifiers=['Programming Language :: Python',
                   'License :: OSI Approved :: BSD License'],
      )
