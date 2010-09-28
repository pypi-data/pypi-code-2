import subprocess

from setuptools import Extension as _Extension

def _combine(list_, dict_=None):
    def _reducer(x, (a, b)):
        x.setdefault(a, []).append(b)
        return x
    return reduce(_reducer, list_, dict_ if dict_ is not None else {})

def _mapoptions(list_, map_, default):
    for i in list_:
        key = map_.get(i[:2])
        if key:
            yield key, i[2:]
        else:
            yield default, i

class Extension(_Extension):
    def __pkgconfig(self, package, option):
        return subprocess.Popen(['pkg-config', option, package],
            stdout=subprocess.PIPE).communicate()[0].split()

    def __libs_for_package(self, package, outdict=None):
        l = {'-L': 'library_dirs',
             '-l': 'libraries', }  # extra_link_args
        default = 'extra_link_args'
        options = self.__pkgconfig(package, '--libs')
        return _combine(_mapoptions(options, l, default), outdict)

    def __cflags_for_package(self, package, outdict=None):
        c = {'-D': 'define_macros',
             '-I': 'include_dirs', }  # extra_compile_flags
        default = 'extra_compile_flags'
        options = self.__pkgconfig(package, '--cflags')
        return _combine(_mapoptions(options, c, default), outdict)

    def __options_for_package(self, package, outdict=None):
        out = {}
        self.__cflags_for_package(package, out)
        self.__libs_for_package(package, out)
        out['define_macros'] = [tuple(i.split('=', 1)) if i.split('=')[1:]
            else (i, None) for i in out.pop('define_macros', [])]
        outdict.update(out)
        return outdict

    def __init__(self, *args, **kwargs):
        packages = kwargs.pop('pkg_config')
        for package in packages:
            options = self.__options_for_package(package, kwargs)
        _Extension.__init__(self, *args, **kwargs)
