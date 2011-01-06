from distutils.core import setup

setup(
name='rlcompleter3',
py_modules=['rlcompleter3'],
version='1.0',
description='another readline completer that also completes function arguments',
author='Glomeron Christophe',
author_email='glomeron.christophe@free.fr',
url='http://glomeron.christophe.free.fr',
license= "GPL 2.1 License",
long_description = """
simply uses <tab> to have completion
if the word is already completed when doing <tab>:
   if the object is a function, the prototype is displayed, and a '(' character is completed
   if the object is of type 'str, int, float, bool', the value of the object is displayed
   if the object a a documentation, the full doc is displayed
""",
     )


