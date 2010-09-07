from distutils.core import setup


setup(
    name='linuxdvb',
    version='0.1',
    license='GPLv2',
    requires=('ctypes',),
    py_modules=('linuxdvb',),

    maintainer='n8fq',
    maintainer_email='jvn8fq@gmail.com',
    url='http://pypi.python.org/pypi/linuxdvb',
    download_url='http://www.electroblog.com/linuxdvb_0.1.tar.gz',
    keywords='linux dvb atsc dcii binding ctypes',
    description='Python bindings for Linux DVB API',
    long_description=open('README'),

    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Video :: Capture',
    ),
)
