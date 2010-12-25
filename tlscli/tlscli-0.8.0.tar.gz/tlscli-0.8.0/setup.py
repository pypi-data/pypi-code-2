from distutils.core import setup
from distutils.command.install import install
from distutils.errors import DistutilsExecError

import os.path

def compile_idl(filename, includes, outputdir):
    print 'compiling %s into %s' % (filename, outputdir)

    try:
        import omniidl.main
        omniidl.main.main(['ignored', '-bpython'] +
                          ['-I' + path for path in includes] +
                          ['-C' + outputdir, filename])
    except ImportError:
        raise DistutilsExecError('omniidl not available')

class generate_corba_stubs(install):
    def run(self):
        install.run(self)
        compile_idl('DsLogAdmin.idl',
                    [os.path.join(self.install_base,
                                  'share', 'idl', 'omniORB', 'COS')],
                    self.install_lib)

setup(
    name='tlscli',
    version='0.8.0',
    author='Thomas Girard',
    author_email='thomas.g.girard@free.fr',
    url='https://launchpad.net/tlscli',
    license='LICENSE.txt',
    description='Text User Interface client for CORBA Telecom Log Service.',
    long_description=open('README.txt').read(),
    scripts=['tlscli'],
    cmdclass={'install': generate_corba_stubs},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ]
)
