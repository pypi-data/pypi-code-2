from glob import fnmatch

from svarga import env, template
from svarga.utils import urljoin

from svargaext import clevercss

@template.global_('clevercss')
def clevercss_(name, path):
    mapping = env.settings.CLEVERCSS[name]
    for source, target in mapping.items():
        if path == source or fnmatch.fnmatch(path, source):
            pth, src, tgt = clevercss.abspats(name, path, source, target)
            clevercss.render(pth, clevercss.deglob(pth, src, tgt))

            url = env.get_static_url(name)
            return urljoin.safe_url_join(url, clevercss.deglob(path, source, target))
    raise Exception("Can't find path %s in %s" % (path, name))
