# -*- coding: utf-8 -*-
import re
from .common import Filler

from typetrainer.i18n import _

name = 'ru'
label = _('Russian')

levels = (
    ('basic', _('Basic')),
    ('advanced', _('Advanced')),
#    ('superb', _('Superb')),
)

def make_lengths_seq(words):
    for t, w in words:
        if t == 'w':
            wlen = len(w)
            yield 'w', wlen
        else:
            yield t, w

def split_to_words(text, level):
    filter_non_word = re.compile(u'(?iu)[^а-я]+')

    charsets = {
        'basic': u'(?iu)[а-я]+',
        'advanced': u'(?iu)[а-я,.:;"!]+'
    }

    if level == 'basic':
        text = text.lower()

    for word in re.findall(charsets[level], text):
        non_word_cars = ',.:;"!'
        esym = None
        for c in non_word_cars:
            if word.endswith(c):
                esym = c
                break

        ssym = '"' if word.startswith('"') else None

        word = filter_non_word.sub('', word).strip("'")
        if word:
            if ssym:
                yield 's', ssym
            yield 'w', word
            if esym:
                yield 's', esym

            yield 's', ' '

def get_filler(text, level):
    words = list(split_to_words(text, level))
    if not words:
        words = list(split_to_words(u'Пустое упражнение. Выберите другое или загрузите '
            u'соответствующий файл', level))
    return Filler(words, make_lengths_seq)