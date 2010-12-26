from glob import fnmatch

from svarga import env, template
from svarga.utils import urljoin

from svargaext.transform import render, abspats, deglob, backends

@template.global_
def transform(backend, name, path):
    mapping = env.settings.TRANSFORM[backend][name]
    for source, target in mapping.items():
        if path == source or fnmatch.fnmatch(path, source):
            pth, src, tgt = abspats(name, path, source, target)
            render(backend, pth, deglob(pth, src, tgt))

            url = env.get_static_url(name)
            return urljoin.safe_url_join(url, deglob(path, source, target))
    raise Exception("Can't find path %s in %s" % (path, name))

def specific_global(backend):
    def inner(name, path):
        return transform(backend, name, path)
    inner.__name__ = backend
    return inner

for backend in backends.BACKENDS:
    template.global_(backend)(specific_global(backend))
