import os

from distutils.core import setup
from distutils.command.install_scripts import install_scripts


CONF_LOCATION = '/etc/chartio.cfg'
PIDFILE_LOCTATION = '/var/run/chartio_connect.pid'
LOGFILE_LOCATION = '/var/log/chartio_connect.log'

class PostInstall(install_scripts):

    def run(self):
        install_scripts.run(self)
        # Touch files as root and make it writeable
        for fi in [CONF_LOCATION, PIDFILE_LOCTATION, LOGFILE_LOCATION]:
            os.system('touch %s' % fi)
            os.system('chmod 666 %s' % fi)


setup(  cmdclass=dict(install_scripts=PostInstall),
        name='chartio',
        version='1.0.2',
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
