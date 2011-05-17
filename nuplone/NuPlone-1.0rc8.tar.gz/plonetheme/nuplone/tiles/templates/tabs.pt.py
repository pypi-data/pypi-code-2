registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _attrs_4464357136 = _loads('(dp1\nVhref\np2\nV${tab/url}\np3\ns.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _attrs_4464357264 = _loads('(dp1\nVid\np2\nVsearch\np3\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_4464356880 = _loads('(dp1\nVclass\np2\nV${tab/class}\np3\ns.')
    _attrs_4464356624 = _loads('(dp1\nVid\np2\nVtabs\np3\ns.')
    _attrs_4464353680 = _loads('(dp1\nVhref\np2\nV${view/home_url}\np3\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4464370768 = _loads('(dp1\nVtype\np2\nVsubmit\np3\ns.')
    _attrs_4464354512 = _loads('(dp1\nVname\np2\nVq\nsVtype\np3\nVtext\np4\nsVid\np5\nVsearchField\np6\ns.')
    _attrs_4464354128 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4464354384 = _loads('(dp1\nVclass\np2\nVsuperImpose\np3\nsVfor\np4\nVsearchField\np5\ns.')
    _attrs_4464357008 = _loads('(dp1\nVid\np2\nVhome\np3\ns.')
    _attrs_4464353872 = _loads('(dp1\nVaction\np2\nV${tools/navroot_url}/@@search\np3\nsVmethod\np4\nVget\np5\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
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
        'nocall:context/@@tools'
        tools = _path(econtext['context'], econtext['request'], False, '@@tools')
        _write(u'\n  ')
        attrs = _attrs_4464356624
        'view/tabs'
        _write(u'<ul id="tabs">\n    ')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'tabs')
        tab = None
        (_tmp1, _tmp2, ) = repeat.insert('tab', _tmp1)
        for tab in _tmp1:
            _tmp2 = (_tmp2 - 1)
            attrs = _attrs_4464356880
            'join(value("_path(tab, request, True, \'class\')"),)'
            _write(u'<li')
            _tmp3 = _path(tab, econtext['request'], True, 'class')
            if (_tmp3 is _default):
                _tmp3 = u'${tab/class}'
            if ((_tmp3 is not None) and (_tmp3 is not False)):
                if (_tmp3.__class__ not in (str, unicode, int, float, )):
                    _tmp3 = unicode(_translate(_tmp3, domain=_domain, mapping=None, target_language=target_language, default=None))
                else:
                    if not isinstance(_tmp3, unicode):
                        _tmp3 = unicode(str(_tmp3), 'UTF-8')
                if ('&' in _tmp3):
                    if (';' in _tmp3):
                        _tmp3 = _re_amp.sub('&amp;', _tmp3)
                    else:
                        _tmp3 = _tmp3.replace('&', '&amp;')
                if ('<' in _tmp3):
                    _tmp3 = _tmp3.replace('<', '&lt;')
                if ('>' in _tmp3):
                    _tmp3 = _tmp3.replace('>', '&gt;')
                if ('"' in _tmp3):
                    _tmp3 = _tmp3.replace('"', '&quot;')
                _write(((' class="' + _tmp3) + '"'))
            _write('>')
            attrs = _attrs_4464357136
            'join(value("_path(tab, request, True, \'url\')"),)'
            _write(u'<a')
            _tmp3 = _path(tab, econtext['request'], True, 'url')
            if (_tmp3 is _default):
                _tmp3 = u'${tab/url}'
            if ((_tmp3 is not None) and (_tmp3 is not False)):
                if (_tmp3.__class__ not in (str, unicode, int, float, )):
                    _tmp3 = unicode(_translate(_tmp3, domain=_domain, mapping=None, target_language=target_language, default=None))
                else:
                    if not isinstance(_tmp3, unicode):
                        _tmp3 = unicode(str(_tmp3), 'UTF-8')
                if ('&' in _tmp3):
                    if (';' in _tmp3):
                        _tmp3 = _re_amp.sub('&amp;', _tmp3)
                    else:
                        _tmp3 = _tmp3.replace('&', '&amp;')
                if ('<' in _tmp3):
                    _tmp3 = _tmp3.replace('<', '&lt;')
                if ('>' in _tmp3):
                    _tmp3 = _tmp3.replace('>', '&gt;')
                if ('"' in _tmp3):
                    _tmp3 = _tmp3.replace('"', '&quot;')
                _write(((' href="' + _tmp3) + '"'))
            u'tab/title'
            _write('>')
            _tmp3 = _path(tab, econtext['request'], True, 'title')
            _tmp = _tmp3
            if (_tmp.__class__ not in (str, unicode, int, float, )):
                try:
                    _tmp = _tmp.__html__
                except:
                    _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
                else:
                    _tmp = _tmp()
                    _write(_tmp)
                    _tmp = None
            if (_tmp is not None):
                if not isinstance(_tmp, unicode):
                    _tmp = unicode(str(_tmp), 'UTF-8')
                if ('&' in _tmp):
                    if (';' in _tmp):
                        _tmp = _re_amp.sub('&amp;', _tmp)
                    else:
                        _tmp = _tmp.replace('&', '&amp;')
                if ('<' in _tmp):
                    _tmp = _tmp.replace('<', '&lt;')
                if ('>' in _tmp):
                    _tmp = _tmp.replace('>', '&gt;')
                _write(_tmp)
            _write(u'</a></li>')
            if (_tmp2 == 0):
                break
            _write(' ')
        _write(u'\n    ')
        attrs = _attrs_4464357008
        _write(u'<li id="home">')
        attrs = _attrs_4464353680
        'join(value("_path(view, request, True, \'home_url\')"),)'
        _write(u'<a')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'home_url')
        if (_tmp1 is _default):
            _tmp1 = u'${view/home_url}'
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = unicode(str(_tmp1), 'UTF-8')
            if ('&' in _tmp1):
                if (';' in _tmp1):
                    _tmp1 = _re_amp.sub('&amp;', _tmp1)
                else:
                    _tmp1 = _tmp1.replace('&', '&amp;')
            if ('<' in _tmp1):
                _tmp1 = _tmp1.replace('<', '&lt;')
            if ('>' in _tmp1):
                _tmp1 = _tmp1.replace('>', '&gt;')
            if ('"' in _tmp1):
                _tmp1 = _tmp1.replace('"', '&quot;')
            _write(((' href="' + _tmp1) + '"'))
        u'tools/site_title'
        _write('>')
        _tmp1 = _path(tools, econtext['request'], True, 'site_title')
        _tmp = _tmp1
        if (_tmp.__class__ not in (str, unicode, int, float, )):
            try:
                _tmp = _tmp.__html__
            except:
                _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
            else:
                _tmp = _tmp()
                _write(_tmp)
                _tmp = None
        if (_tmp is not None):
            if not isinstance(_tmp, unicode):
                _tmp = unicode(str(_tmp), 'UTF-8')
            if ('&' in _tmp):
                if (';' in _tmp):
                    _tmp = _re_amp.sub('&amp;', _tmp)
                else:
                    _tmp = _tmp.replace('&', '&amp;')
            if ('<' in _tmp):
                _tmp = _tmp.replace('<', '&lt;')
            if ('>' in _tmp):
                _tmp = _tmp.replace('>', '&gt;')
            _write(_tmp)
        _write(u'</a></li>\n    ')
        attrs = _attrs_4464357264
        _write(u'<li id="search">\n      ')
        attrs = _attrs_4464353872
        'join(value("_path(tools, request, True, \'navroot_url\')"), u\'/@@search\')'
        _write(u'<form method="get"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'navroot_url'), '/@@search', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/navroot_url}/@@search'
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = unicode(str(_tmp1), 'UTF-8')
            if ('&' in _tmp1):
                if (';' in _tmp1):
                    _tmp1 = _re_amp.sub('&amp;', _tmp1)
                else:
                    _tmp1 = _tmp1.replace('&', '&amp;')
            if ('<' in _tmp1):
                _tmp1 = _tmp1.replace('<', '&lt;')
            if ('>' in _tmp1):
                _tmp1 = _tmp1.replace('>', '&gt;')
            if ('"' in _tmp1):
                _tmp1 = _tmp1.replace('"', '&quot;')
            _write(((' action="' + _tmp1) + '"'))
        _write(u'>\n        ')
        attrs = _attrs_4464354128
        _write(u'<fieldset>\n          ')
        attrs = _attrs_4464354384
        u"%(translate)s('menu_search', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<label for="searchField" class="superImpose">')
        _result = _translate('menu_search', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Search')
        _write(u'</label>')
        attrs = _attrs_4464354512
        _write(u'<input type="text" name="q" id="searchField" />')
        attrs = _attrs_4464370768
        u"%(translate)s('button_submit', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<button type="submit">')
        _result = _translate('button_submit', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Submit')
        _write(u'</button>\n        </fieldset>\n      </form>\n    </li>\n  </ul>\n')
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/tiles/templates/tabs.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
