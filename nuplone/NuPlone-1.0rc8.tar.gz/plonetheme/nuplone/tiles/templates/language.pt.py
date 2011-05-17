registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_4501846800 = _loads('(dp1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4501846928 = _loads('(dp1\n.')
    _attrs_4501846736 = _loads('(dp1\nVclass\np2\nVportletContent\np3\ns.')
    _attrs_4501847248 = _loads("(dp1\nVhref\np2\nV${context_url}/@@switch-language?language=${language/code}\np3\nsVclass\np4\nV${python:'current' if language['code']==current_language else None}\np5\ns.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4501846544 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\nsVclass\np4\nVportlet\np5\nsVid\np6\nVportletLanguage\np7\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
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
        _tmp_domain0 = _domain
        u"'nuplone'"
        _domain = 'nuplone'
        'view/languages'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'languages')
        if _tmp1:
            pass
            attrs = _attrs_4501846544
            _write(u'<div xmlns="http://www.w3.org/1999/xhtml" class="portlet" id="portletLanguage">\n  ')
            attrs = _attrs_4501846800
            u"%(translate)s('portlet_languages', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h3>')
            _result = _translate('portlet_languages', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Languages')
            'context/absolute_url'
            _write(u'</h3>\n  ')
            context_url = _path(econtext['context'], econtext['request'], True, 'absolute_url')
            'view/current_language'
            current_language = _path(econtext['view'], econtext['request'], True, 'current_language')
            attrs = _attrs_4501846736
            _write(u'<div class="portletContent">\n    ')
            attrs = _attrs_4501846928
            'view/languages'
            _write(u'<p>')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'languages')
            language = None
            (_tmp1, _tmp2, ) = repeat.insert('language', _tmp1)
            for language in _tmp1:
                _tmp2 = (_tmp2 - 1)
                _write('')
                attrs = _attrs_4501847248
                'join(value(\'_path(context_url, request, True, )\'), u\'/@@switch-language?language=\', value("_path(language, request, True, \'code\')"))'
                _write(u'<a')
                _tmp3 = ('%s%s%s' % (_path(context_url, econtext['request'], True), '/@@switch-language?language=', _path(language, econtext['request'], True, 'code'), ))
                if (_tmp3 is _default):
                    _tmp3 = u'${context_url}/@@switch-language?language=${language/code}'
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
                'join(value("\'current\' if language[\'code\']==current_language else None"),)'
                _tmp3 = ('current' if (language['code'] == current_language) else None)
                if (_tmp3 is _default):
                    _tmp3 = u"${python:'current' if language['code']==current_language else None}"
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
                try:
                    u'language/native'
                    _tmp3 = _path(language, econtext['request'], True, 'native')
                except Exception, e:
                    u'language/name'
                    _tmp3 = _path(language, econtext['request'], True, 'name')
                
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
                u"not(_path(repeat, request, True, 'language', 'end'))"
                _write(u'</a>')
                _tmp3 = not _path(repeat, econtext['request'], True, 'language', 'end')
                if _tmp3:
                    pass
                    _write(u' | ')
                if (_tmp2 == 0):
                    break
                _write(' ')
            _write(u'</p>\n  </div>\n')
            _write(u'</div>')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/tiles/templates/language.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
