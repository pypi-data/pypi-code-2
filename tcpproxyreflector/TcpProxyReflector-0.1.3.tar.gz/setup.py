# /bin/env python
# setup.py
# (c) alain.spineux@gmail.com

import sys, os
try: 
  from setuptools import setup 
except ImportError: 
  from distutils.core import setup 

basename='tcpproxyreflector'
# retrieve $version
version=''
for line in open('tcprlib/tcpr.py'):
    if line.startswith("__version__="):
        version=line[13:].rstrip()[:-1]
        break

if not version:
    print 
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    print '!                                             !'
    print '!            VERSION NOT FOUND                !'
    print '!                                             !'
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    sys.exit(1)

print 'VERSION', version

try:
    from py2exe.build_exe import py2exe
except ImportError:
    pass
else:
    class build_zip(py2exe):
        """This class inherit from py2exe, builds the exe file(s), then creates a ZIP file."""
        def run(self):
            
            import zipfile
            # initialize variables and create appropriate directories in 'buid' directory
            # please don't change 'dist_dir' in setup()
             
            orig_dist_dir=self.dist_dir
            self.mkpath(orig_dist_dir)
            zip_filename=os.path.join(orig_dist_dir, '%s-%s-win32.zip' % (self.distribution.metadata.name, self.distribution.metadata.version,))
            bdist_base=self.get_finalized_command('bdist').bdist_base
            dist_dir=os.path.join(bdist_base, '%s-%s' % (self.distribution.metadata.name, self.distribution.metadata.version, ))
            self.dist_dir=dist_dir
            print 'dist_dir is %s' % (dist_dir, )

            # let py2exe do it's work.
            py2exe.run(self)
            
            # remove zipfile if exists
            if os.path.exists(zip_filename):
                os.unlink(zip_filename)
            
            # create the zipfile
            print 'Building zip file %s' % (zip_filename, )
            zfile=zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk(dist_dir):
                for f in files:
                    filename=os.path.join(root, f)
                    zfile.write(filename, os.path.relpath(filename, bdist_base))
                    
            # zfile.writestr('EGG-INFO/PKG-INFO', 'This file is required by PyPI to allow upload')
            zfile.close()
            # If this file is uploaded, it is used by easy_install or pip as a source file
            # self.distribution.dist_files.append(('bdist_dumb', '2.3', zip_filename))

extra_options = {}
doc_dir='share/doc/%s-%s' % (basename, version)

cmdclass = {}

if 'py2exe' in sys.argv and os.name=='nt':
    doc_dir='doc'
    cmdclass = {"py2exe": build_zip}
    py2exe_options =  { # 'ascii': True, # exclude encodings
                        'packages':[], 
                        'dll_excludes': ['w9xpopen.exe'], # no support for W98 
                        'compressed':True, 
                        # 'dist_dir': ????  # !!! DONT CHANGE distdir HERE 
                        # exclude big and unused python packages from the binary
                        'excludes': [ 'email', '_ssl', 'difflib', 'doctest', 'locale', 'calendar', 'pdb'],
                        }
    extra_options = { 'console': ['tcpr', ],  # list of scripts to convert into console exes
                      'windows': [],          # list of scripts to convert into gui exes
                      'options': { 'py2exe': py2exe_options, } ,
                    }
    if '--single-file' in sys.argv[1:]:
        sys.argv.remove('--single-file')
        py2exe_options.update({ 'bundle_files': 1, })
        extra_options.update({ 'zipfile': None, }) # don't build a separate zip file with all libraries, put them all in the .exe  

    
data_files=[ 
             (doc_dir, [ 'README.txt', 'Changelog.txt', 'TODO.txt', 'LICENSE.txt', 'sample.ini',]),
             (os.path.join(doc_dir, 'srplib'), [ os.path.join('tcprlib', 'srplib', 'README.txt'), ]),
           ]
           
if 'bdist_egg' in sys.argv:
    data_files.append(('', ['__main__.py', ]))

if 'sdist' in sys.argv:
    data_files.append((os.path.join(doc_dir, 'contrib'), [ os.path.join('contrib', 'SRPSocket.tgz'), ]))

setup(name='TcpProxyReflector',
      version=version, 
      author='Alain Spineux',
      author_email='alain.spineux@gmail.com',
      url='http://blog.magiksys.net/software/tcp-proxy-reflector',
      description='Set of libraries and programs to access internal network resources from outside the LAN via a remote server, without any port forwarding',
      long_description='This package include a library and a fully functional client and server application. '
                       'The server acts as a proxy sitting between a user and a client. The user activates ' 
                       'a forwarder on the server to access one of the resource available through the '
                       'connected client. This forwarder forwards new connections to the client. Then the '
                       'client forwards the connection up to the local resource. '
                       'The library and programs manage authentication and some securities. '
                       'A .exe for windows and a runnable .egg that don''t need installation are '
                       'available from the site at http://blog.magiksys.net/software/tcp-proxy-reflector',
      license='GPL',
      # package_dir={'tcprlib.srplib': 'tcprlib.srplib'},
      packages=[ 'tcprlib', 'tcprlib.srplib'  ],
      scripts=[ 'tcpr' ],
      data_files=data_files,
      classifiers=["Development Status :: 4 - Beta",
                  "Intended Audience :: Developers",
                  "License :: OSI Approved :: GNU General Public License (GPL)",
                  "Operating System :: OS Independent",
                  "Topic :: System :: Networking",
                  "Topic :: Internet",
                  ],

      cmdclass = cmdclass,

      **extra_options)
