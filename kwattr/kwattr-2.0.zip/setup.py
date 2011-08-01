from distutils.core import setup

ld = '''
script::

    from kwattr import kwattr

    @kwattr.wait.chdir.min.max.hide
    def run(*args, **kwargs):
        return args, kwargs

    @kwattr.all.dirs
    def scan(arg, idir=False, ifile=True, all=False, dirs=False):
        return arg, idir, ifile, all, dirs

    print run.wait('sample.exe')
    print run('sample.exe')
    print run.wait.chdir('sample.exe')

out::

    (('sample.exe',), {'max': False, 'chdir': False, 'hide': False, 'min': False, 'wait': True})
    (('sample.exe',), {'max': False, 'chdir': False, 'hide': False, 'wait': False, 'min': False})
    (('sample.exe',), {'max': False, 'chdir': True, 'hide': False, 'min': False, 'wait': True})

'''

setup(name='kwattr',
    version='2.0',
    packages=['kwattr'],
    license = 'Python license',
    author_email = 'ivan.bykov@gmail.com',
    author = 'Ivan Bykov',
    url = '',
    platforms = 'python 2.7',
    description = 'decorator: make keywords arguments of bool values from function attributes',
    long_description = ld,
    classifiers = [
        'License :: OSI Approved :: Python Software Foundation License',
        'Natural Language :: Russian',
        ]
    )
