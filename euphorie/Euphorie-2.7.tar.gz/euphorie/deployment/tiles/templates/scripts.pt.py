registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4464616848 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4464600528 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u'_init_stream()'
        (_out, _write, ) = _init_stream()
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        _write(u'\n  ')
        attrs = _attrs_4464600528
        u"%(translate)s('title_toggle_navtree', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<script type="text/javascript">\nvar twisty_title = \'')
        _result = _translate('title_toggle_navtree', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Show older versions')
        u"%(translate)s('text_toggle_navtree', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u"',\n    twisty_text = '")
        _result = _translate('text_toggle_navtree', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Toggle')
        _write(u"';\n//  ")
        attrs = _attrs_4464616848
        _write(u'<![CDATA[\n$(document).ready(function() {\n\n    $(".navigationTree-folderish > li:has(ul)").each(function() {\n      $("<span>").addClass("toggle").attr("title", twisty_title).text(twisty_text).prependTo(this);\n    });\n});\n\n$(".navigationTree-folderish .toggle").live("click", function() {\n    var $toggle = $(this);\n\n    $toggle.toggleClass("open");\n    if ($toggle.hasClass("open")) {\n      $toggle.parent().find(">ul").slideDown();\n    } else {\n      $toggle.parent().find(">ul").slideUp();\n    }\n});\n// ]]>\n  </script>\n')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/Euphorie/euphorie/deployment/tiles/templates/scripts.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
