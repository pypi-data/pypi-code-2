import ws_grek
import ws_latn
import ws_en
import ws_tr
import ws_copt

def transliterate_name(lang, name_utf8):
    """Transliterate into modern Roman."""
    wsystem = lang.lower()
    if isinstance(name_utf8, unicode):
        name = name_utf8[:]
    else:
        name = unicode(name_utf8, 'utf-8')
    if wsystem == 'en':
        return ws_en.transliterate(name)
    elif wsystem == 'grc' or wsystem == 'la-grek':
        return ws_grek.transliterate(name)
    elif wsystem == 'la' or wsystem == 'grc-latn':
        return ws_latn.transliterate(name)
    elif wsystem == 'tr':
        return ws_tr.transliterate(name)
    elif wsystem == 'cop':
        return ws_copt.transliterate(name)
    else:
        raise ValueError, 'Unsupported writing system (%s)' % lang
    
