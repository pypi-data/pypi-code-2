import os

from distutils.core import setup
from distutils.command.install_data import install_data


CONF_LOCATION = '/etc/chartio.cfg'

class PostInstall(install_data):

    def run(self):
        distutils.command.install.run(self)
        # Touch config file, as root, and make it writeable
        os.system('touch %s' % CONF_LOCATION)
        os.system('chmod 666 foo')

setup(name='chartio',
        cmdclass=dict(install=PostInstall),
        version='1.0',
        scripts=['chartio_setup.py', 'chartio_connect.py'],
        classifiers = ['Environment :: Console',
                       'Intended Audience :: System Administrators',
                       'License :: OSI Approved :: BSD License',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 2.4',
                       'Programming Language :: Python :: 2.5',
                       'Programming Language :: Python :: 2.6',
                       'Programming Language :: Python :: 2.7',
                       'Topic :: System :: Monitoring',
                       'Topic :: Database',
                       'Topic :: Database :: Database Engines/Servers',
                       ],
        url="http://chart.io/", 
        author="chart.io",
        author_email="support@chart.io",
        description="Setup wizard and connection client for connecting MySQL databases to chart.io",
)
