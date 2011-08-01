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
