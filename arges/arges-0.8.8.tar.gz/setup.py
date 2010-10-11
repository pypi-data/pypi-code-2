import os, sys, glob, fnmatch
import distutils.command.install_data
from distutils.core import setup, Extension

version = '0.8.8'

#find files functions were taken from http://wiki.python.org/moin/Distutils/Tutorial

def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

# Specializations of some distutils command classes
class wx_smart_install_data(distutils.command.install_data.install_data):
    """need to change self.install_dir to the actual library dir"""
    def run(self):
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return distutils.command.install_data.install_data.run(self)
    
def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    def walk_helper(arg, dirname, files):
        if '.svn' in dirname:
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                    names.append(filename)
        if names:
            lst.append( (dirname, names ) )

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

files = find_data_files('arges/data/', '*.*')

setup(name='arges',
      version=version,
      long_description=open('README.txt').read(),
      description='Simple and multi platform automated testing and tasks execution tool, that can be used straight from the command line.',

      keywords='automated testing, qa, selenium, testing, bdd, tdd',
      author='Adrian Deccico',
      author_email='deccico@gmail.com',
      url='http://http://code.google.com/p/arges/',
      
      license='Apache License 2.0',
      
      packages=['arges', 'arges.argestools', 'arges.argestools.api', 'arges.argestools.argesfiles', 
                'arges.argestools.runner', 'arges.thirdparty', 'arges.thirdparty.selenium', 'arges.util'],

      ## Causes the data_files to be installed into the modules directory.
      ## Override some of the default distutils command classes with my own.
      cmdclass = { 'install_data':    wx_smart_install_data },              
      
      data_files = files,       
      
      scripts=['bin/arges'],

      #classifiers from http://pypi.python.org/pypi?:action=list_classifiers
      classifiers = [
                     'Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Apache Software License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Software Development :: Build Tools',                   
                     'Topic :: Software Development :: Interpreters',                   
                     'Topic :: Software Development :: Libraries',                   
                     'Topic :: Software Development :: Quality Assurance',
                     'Topic :: Software Development :: Testing',                   
                     'Topic :: Software Development :: Libraries :: Python Modules',
                   ],      
      )
