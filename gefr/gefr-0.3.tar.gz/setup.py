
from jip.dist import setup
from gefr import gefr_version    

requires_java = {
            'dependencies':[
                ('org.slf4j', 'slf4j-api', '1.6.1'),
                ('org.slf4j', 'slf4j-log4j12', '1.6.1'),
                ('info.sunng.soldat', 'soldat', '1.0-SNAPSHOT'),
                ('org.apache.mina', 'mina-core', '2.0.2'),
                ('org.eclipse.jetty', 'jetty-server', '7.4.2.v20110526'),
                ('org.jboss.netty', 'netty', '3.2.4.Final')
            ],
            'repositories':[
                ('sonatype-oss-snapshot', 'http://oss.sonatype.org/content/repositories/snapshots/'),
            ]
        }

setup(
    name="gefr",
    version=gefr_version,
    author="Sun Ning",
    author_email="classicning@gmail.com",
    url="https://bitbucket.org/sunng/gefr",
    description="A suite of WSGI bridges to Java servers.",
    license='mit',
    packages=['gefr', 'gefr.backends'],
#    py_modules=['gefr.core', 'gefr.wsgi', 'gefr.backends.soldat', 'gefr.backends.mina'],
    install_requires=['jip'],
    requires_java=requires_java,
    long_description="""
    A suite of WSGI bridges to Java servers.
    
    """,
    classifiers=['Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Java',
        'Environment :: Web Environment',
        'Operating System :: POSIX']
)


