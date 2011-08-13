


from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
import os, sys
import shutil

required_python_version = '2.6'

classifiers = """
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
Intended Audience :: System Administrators
License :: OSI Approved :: BSD License
Operating System :: OS Independent
Programming Language :: Python :: 2
Topic :: Text Processing
Topic :: Software Development :: Build Tools
Topic :: Utilities
"""
classifier_list = [c for c in classifiers.split("\n") if c]

setup_args = dict(
   name='j2', 
   version='1.2',
   author = 'John Cavanaugh',
   author_email = 'cavanaughwww+open@gmail.com',
   description = 'cmdline text templating & rendering tool using Jinja2',
   long_description="""
j2 is commandline text templating & rendering tool, it brings the power of the Jinja2 engine to general
purpose text compilation. The tool excels at the various situations where you need to compile/generate
text files as part of a build system or other types of automation process (sysadmin to configuration
files etc)
""",
   keywords = 'text templating cmdline',
   license = 'BSD',
   scripts = ['j2'],
   url = 'https://bitbucket.org/cavanaug/j2',
   classifiers = classifier_list,
   install_requires=[ 'Jinja2' ]
   )

def main():
    if sys.version < required_python_version:
       print "Requires Python %s or later" % (required_python_version)

    # Force scripts into bin even on windows
    for scheme in INSTALL_SCHEMES.values():
       scheme['scripts']='$base/bin'


    if sys.platform == 'win32':
        shutil.copyfile('j2', 'j2.py')
        setup_args['scripts']=['j2.py']

    dist=setup(**setup_args)

if __name__ == "__main__":
   main()

