import os, os.path as op
import glob
import logging

from svarga import env
import clevercss


logger = logging.getLogger('svargaext.clevercss')


class CleverCssException(Exception):
    pass


def needs_update(source, target):
    if not op.exists(target):
        return True
    return os.stat(source)[8] > os.stat(target)[8]


def abspats(name, *pats):
    return [op.join(env.settings.STATIC_URLS[name][1], path) for path in pats]


def deglob(fn, source, target):
    if not '*' in source:
        return target
    if not '*' in target:
        raise CleverCssException('No wildcard in target specification: %s' % target)

    head, tail = source.split('*')
    if not (fn.startswith(head) and fn.endswith(tail)):
        raise CleverCssException("Can't use deglobbing magic!")

    heart = fn[len(head):-len(tail)]
    return target.replace('*', heart)


def render(source, target):
    if not op.exists(source):
        raise CleverCssException("Input file '%s' does not exist" % source)

    if not needs_update(source, target):
        logger.info("%s does't need update", source)
        return

    target_path = op.dirname(target)
    if not op.exists(target_path):
        os.makedirs(target_path)

    logger.info('Compiling %s to %s', source, target)

    file(target, 'w').write(clevercss.convert(file(source, 'r').read()))


def process():
    for name, mapping in env.settings.SASS.items():
        for source, target in mapping.items():
            source, target = abspats(name, source, target)
            for fn in glob.glob(source):
                render(fn, deglob(fn, source, target))
