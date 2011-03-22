from MoinMoin.theme import modernized

class Theme(modernized.Theme):
    name = "heat"

    _ = lambda x: x     # We don't have gettext at this moment, so we fake it
    icons = {
        # key         alt                        icon filename      w   h
        # FileAttach
        'attach':     ("%(attach_count)s",       "moin-attach.png", 16, 16),
        'info':     ("[INFO]",       "moin-info.png", 16, 16),
        'attachimg':  (_("[ATTACH]"),            "attach.png",      32, 32),
        # RecentChanges
        'rss':        (_("[RSS]"),               "moin-rss.png",    16, 16),
        'deleted':    (_("[DELETED]"),           "moin-deleted.png",16, 16),
        'updated':    (_("[UPDATED]"),           "moin-updated.png",16, 16),
        'renamed':    (_("[RENAMED]"),           "moin-renamed.png",16, 16),
        'conflict':   (_("[CONFLICT]"),          "moin-conflict.png", 16, 16),
        'new':        (_("[NEW]"),               "moin-new.png",    16, 16),
        'diffrc':     (_("[DIFF]"),              "moin-diff.png",   16, 16),
        # General
        'bottom':     (_("[BOTTOM]"),            "moin-bottom.png", 16, 16),
        'top':        (_("[TOP]"),               "moin-top.png",    16, 16),
        'www':        ("[WWW]",                  "moin-www.png",    16, 16),
        'mailto':     ("[MAILTO]",               "moin-email.png",  16, 16),
        'news':       ("[NEWS]",                 "moin-news.png",   16, 16),
        'telnet':     ("[TELNET]",               "moin-telnet.png", 16, 16),
        'ftp':        ("[FTP]",                  "moin-ftp.png",    16, 16),
        'file':       ("[FILE]",                 "moin-ftp.png",    16, 16),
        # search forms
        'searchbutton': ("[?]",                  "moin-search.png", 16, 16),
        'interwiki':  ("[%(wikitag)s]",          "moin-inter.png",  16, 16),

        # smileys (this is CONTENT, but good looking smileys depend on looking
        # adapted to the theme background color and theme style in general)
        #vvv    ==      vvv  this must be the same for GUI editor converter
        'X-(':        ("X-(",                    'angry.png',       16, 16),
        ':D':         (":D",                     'biggrin.png',     16, 16),
        '<:(':        ("<:(",                    'frown.png',       16, 16),
        ':o':         (":o",                     'redface.png',     16, 16),
        ':(':         (":(",                     'sad.png',         16, 16),
        ':)':         (":)",                     'smile.png',       16, 16),
        'B)':         ("B)",                     'smile2.png',      16, 16),
        ':))':        (":))",                    'smile3.png',      16, 16),
        ';)':         (";)",                     'smile4.png',      16, 16),
        '/!\\':       ("/!\\",                   'alert.png',       16, 16),
        '<!>':        ("<!>",                    'attention.png',   16, 16),
        '(!)':        ("(!)",                    'idea.png',        16, 16),
        ':-?':        (":-?",                    'tongue.png',      16, 16),
        ':\\':        (":\\",                    'ohwell.png',      16, 16),
        '>:>':        (">:>",                    'devil.png',       16, 16),
        '|)':         ("|)",                     'tired.png',       16, 16),
        ':-(':        (":-(",                    'sad.png',         16, 16),
        ':-)':        (":-)",                    'smile.png',       16, 16),
        'B-)':        ("B-)",                    'smile2.png',      16, 16),
        ':-))':       (":-))",                   'smile3.png',      16, 16),
        ';-)':        (";-)",                    'smile4.png',      16, 16),
        '|-)':        ("|-)",                    'tired.png',       16, 16),
        '(./)':       ("(./)",                   'checkmark.png',   16, 16),
        '{OK}':       ("{OK}",                   'thumbs-up.png',   16, 16),
        '{X}':        ("{X}",                    'icon-error.png',  16, 16),
        '{i}':        ("{i}",                    'icon-info.png',   16, 16),
        '{1}':        ("{1}",                    'prio1.png',       15, 13),
        '{2}':        ("{2}",                    'prio2.png',       15, 13),
        '{3}':        ("{3}",                    'prio3.png',       15, 13),
        '{*}':        ("{*}",                    'star_on.png',     16, 16),
        '{o}':        ("{o}",                    'star_off.png',    16, 16),
    }
    del _

def execute(request):
    return Theme(request)
