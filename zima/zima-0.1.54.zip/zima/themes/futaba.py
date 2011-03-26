# -*- coding: utf-8 -*-
from random import randint
from datetime import datetime

# Общее
id = lambda x:x

# Пути
path = lambda p: cfg.prefix + p

staticPath = lambda fn: '%s/%s' % (cfg.staticUrl, fn)
deletePath = lambda : path('delete')
tailPath = lambda : path('tail')
thumbPath = lambda name: cfg.prefix +\
                    cfg.attaches.thumbs.pathUrl+''.join(name)
imgPath = lambda name: cfg.prefix +\
                    cfg.attaches.pathUrl+''.join(name)

# Заголовки 
headTitle = id
h1Title = id

# Капча 
def captchaUrl(s):
    if cfg.captcha:
        return '%s?%s' % (path(cfg.captcha.url), 
                          randint(0, 1 << 30))
    else:
        return ''

# Нити
def omitted(omittedPosts, omittedAttaches):
    if omittedPosts:
        return '%d posts and %d attaches omitted.' % (
            omittedPosts, omittedAttaches)
    else:
        return ''

def hackop(op, inthread):
    if inthread:
        return op
    op = op.copy()
    op['thlink'] = cfg.reflink('', op['parent'])
    return op

postWrap = lambda obj: {'postWrap': obj}

# Сообщения
formatTs = lambda ts: datetime.fromtimestamp(ts).\
    strftime("%A %d. %B %Y %H:%M:%S")

reflink = cfg.reflink
reftitle = cfg.reftitle

markup = lambda a,b: b

# Картинки
w = lambda a: a[0]
h = lambda a: a[1]
prettyName = lambda name: name[1]
imgSize = lambda sz: len(sz) > 1 and '%d&times;%d' % (sz[1][0], sz[1][1]) or ''
fileSize = lambda sz: cfg.l10n.sz(sz[0])
