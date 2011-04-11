import os, os.path as op
import glob
import logging

from svarga import env

from svargaext.transform.backends import BACKENDS


logger = logging.getLogger(__name__)


class TransformException(Exception):
    pass


def abspats(name, *pats):
    return [op.join(env.settings.STATIC_URLS[name][1], path) for path in pats]


def deglob(fn, source, target):
    if not '*' in source:
        return target
    if not '*' in target:
        raise TransformException('No wildcard in target specification: %s' % target)

    head, tail = source.split('*')
    if not (fn.startswith(head) and fn.endswith(tail)):
        raise TransformException("Can't use deglobbing magic!")

    heart = fn[len(head):-len(tail)]
    return target.replace('*', heart)


def render(backend, source, target):
    if not op.exists(source):
        raise TransformException("Input file '%s' does not exist" % source)

    if op.exists(target):
        mtime = os.stat(target).st_mtime
        if os.stat(source).st_mtime < mtime:
            logger.info("%s does't need update", source)
            return mtime

    target_path = op.dirname(target)
    if not op.exists(target_path):
        os.makedirs(target_path)

    logger.info('Compiling %s to %s', source, target)

    output = BACKENDS[backend](file(source, 'r').read())
    file(target, 'w').write(output)

    return os.stat(target).st_mtime


def process():
    for backend, rules in env.settings.TRANSFORM.items():
        for name, mapping in rules.items():
            for source, target in mapping.items():
                source, target = abspats(name, source, target)
                for fn in glob.glob(source):
                    render(backend, fn, deglob(fn, source, target))
