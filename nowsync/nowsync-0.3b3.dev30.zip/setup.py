try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    
extra = {}

try:
    file = open('README.rst', 'rt')
    content = file.read()
    file.close()
    extra['long_description'] = content
except IOError:
    pass

def getRevision(path=None):
    """Get revision by path 
    
    """
    import os
    try:
        from mercurial import ui, hg
        from mercurial.error import RepoError
    except ImportError:
        return
    
    if path is None:
        path=os.curdir
    
    path = os.path.abspath(path)
    tail = True
    while tail:
        try:
            repo = hg.repository(ui.ui(), path)
        except RepoError:
            pass
        else:
            return repo['.'].rev()
        path, tail = os.path.split(path)
    return

# current version
version = '0.3b3'
rev = getRevision()
if rev is not None:
    version += '.dev%s' % rev

setup(name='nowsync',
    # follow http://www.python.org/dev/peps/pep-0386/
    version=version,
    description='A set of tool for synchronizing local modification to remote' 
                'WSGI server, makes life of designer easier',
    author='Victor Lin',
    author_email='bornstub@gmail.com',
    url='https://bitbucket.org/victorlin/nowsync',
    license='MIT',
    packages=find_packages(),
    entry_points = {
        'console_scripts': [ 
            'nowsync_server = nowsync.scripts.commands:run_server',
            'nowsync_client = nowsync.scripts.commands:run_client',
        ]
    },
    install_requires=[
        'setuptools',
        'Flask',
        'Flask-Genshi',
        'Watchdog',
        'Blinker',
        'httplib2',
        # for python2.5
        'simplejson'
    ],
    package_data={
        'nowsync': [
            'templates/*',
            'static/*'
            '*.yaml'
        ]
    }, 
    **extra
)
