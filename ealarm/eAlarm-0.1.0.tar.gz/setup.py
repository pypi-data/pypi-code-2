from distutils.core import setup

setup(
    name='eAlarm',
    version='0.1.0',
    author='x.seeks',
    author_email='x.seeks@gmail.com',
    packages=['ealarm',],
    scripts=['bin/ealarm'],
    data_files = [('/usr/local/share/ealarm',['ring.wav', 'ring_digital.wav'])],
    url='http://pypi.python.org/pypi/eAlarm',
    license='GPL3, see LICENSE.txt',
    description='A command-line alarm clock.',
    long_description=open('README.txt').read(),
)
