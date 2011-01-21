# -*- coding: utf-8 -*-

# All accented characters in the Unicode Latin-1 Supplement except
# for the Scandinavian å and the German umlauts ä, ö, and ü, which
# are letters in their own right.

GERMAN_ACCENTS = {
    ord(u'À'): ord(u'A'),   ord(u'à'): ord(u'a'),
    ord(u'Á'): ord(u'A'),   ord(u'á'): ord(u'a'),
    ord(u'Â'): ord(u'A'),   ord(u'â'): ord(u'a'),
    ord(u'Ã'): ord(u'A'),   ord(u'ã'): ord(u'a'),
    ord(u'Ç'): ord(u'C'),   ord(u'ç'): ord(u'c'),
    ord(u'È'): ord(u'E'),   ord(u'è'): ord(u'e'),
    ord(u'É'): ord(u'E'),   ord(u'é'): ord(u'e'),
    ord(u'Ê'): ord(u'E'),   ord(u'ê'): ord(u'e'),
    ord(u'Ë'): ord(u'E'),   ord(u'ë'): ord(u'e'),
    ord(u'Ì'): ord(u'I'),   ord(u'ì'): ord(u'i'),
    ord(u'Í'): ord(u'I'),   ord(u'í'): ord(u'i'),
    ord(u'Î'): ord(u'I'),   ord(u'î'): ord(u'i'),
    ord(u'Ï'): ord(u'I'),   ord(u'ï'): ord(u'i'),
    ord(u'Ñ'): ord(u'N'),   ord(u'ñ'): ord(u'n'),
    ord(u'Ò'): ord(u'O'),   ord(u'ò'): ord(u'o'),
    ord(u'Ó'): ord(u'O'),   ord(u'ó'): ord(u'o'),
    ord(u'Ô'): ord(u'O'),   ord(u'ô'): ord(u'o'),
    ord(u'Õ'): ord(u'O'),   ord(u'õ'): ord(u'o'),
    ord(u'Ù'): ord(u'U'),   ord(u'ù'): ord(u'u'),
    ord(u'Ú'): ord(u'U'),   ord(u'ú'): ord(u'u'),
    ord(u'Û'): ord(u'U'),   ord(u'û'): ord(u'u'),
    ord(u'Ý'): ord(u'Y'),   ord(u'ý'): ord(u'y'),
    ord(u'Ÿ'): ord(u'Y'),   ord(u'ÿ'): ord(u'y'),
}

# All of the above plus a, o, and u with diaresis.

LATIN_ACCENTS = {
    ord(u'Ä'): ord(u'A'),   ord(u'ä'): ord(u'a'),
    ord(u'Ö'): ord(u'O'),   ord(u'ö'): ord(u'o'),
    ord(u'Ü'): ord(u'U'),   ord(u'ü'): ord(u'u'),
}
LATIN_ACCENTS.update(GERMAN_ACCENTS)
