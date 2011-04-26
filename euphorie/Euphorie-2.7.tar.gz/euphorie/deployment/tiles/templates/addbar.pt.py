registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4519056656 = _loads('(dp1\nVhref\np2\nV${context/absolute_url}/@@edit\np3\nsVclass\np4\nVbutton floatBefore\np5\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4519056528 = _loads('(dp1\nVclass\np2\nVbuttonBar\np3\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4519056720 = _loads('(dp1\nVhref\np2\nV${factory/url}\np3\nsVtitle\np4\nV${factory/description}\np5\nsVclass\np6\nVbutton floatAfter\np7\ns.')
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
        u"'euphorie'"
        _domain = 'euphorie'
        _write('')
        attrs = _attrs_4519056528
        'view/can_edit'
        _write(u'<div class="buttonBar">\n  ')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'can_edit')
        if _tmp1:
            pass
            attrs = _attrs_4519056656
            'join(value("_path(context, request, True, \'absolute_url\')"), u\'/@@edit\')'
            _write(u'<a class="button floatBefore"')
            _tmp1 = ('%s%s' % (_path(econtext['context'], econtext['request'], True, 'absolute_url'), '/@@edit', ))
            if (_tmp1 is _default):
                _tmp1 = u'${context/absolute_url}/@@edit'
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
            u"%(translate)s('button_edit', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write('>')
            _result = _translate('button_edit', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Edit')
            _write(u'</a>')
        'view/actions'
        _write(u'\n  ')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'actions')
        factory = None
        (_tmp1, _tmp2, ) = repeat.insert('factory', _tmp1)
        for factory in _tmp1:
            _tmp2 = (_tmp2 - 1)
            attrs = _attrs_4519056720
            'join(value("_path(factory, request, True, \'url\')"),)'
            _write(u'<a class="button floatAfter"')
            _tmp3 = _path(factory, econtext['request'], True, 'url')
            if (_tmp3 is _default):
                _tmp3 = u'${factory/url}'
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
            'join(value("_path(factory, request, True, \'description\')"),)'
            _tmp3 = _path(factory, econtext['request'], True, 'description')
            if (_tmp3 is _default):
                _tmp3 = u'${factory/description}'
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
                _write(((' title="' + _tmp3) + '"'))
            u'{}'
            _write('>')
            _mapping_4519056720 = {}
            u'True'
            _tmp3 = True
            if _tmp3:
                pass
                _tmp_out2 = _out
                _tmp_write2 = _write
                u'_init_stream()'
                (_out, _write, ) = _init_stream()
                u'factory/title'
                _tmp4 = _path(factory, econtext['request'], True, 'title')
                _tmp = _tmp4
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
                u'%(out)s.getvalue()'
                _mapping_4519056720['typename'] = _out.getvalue()
                _write = _tmp_write2
                _out = _tmp_out2
            u"%(translate)s('button_add_factory', domain=%(domain)s, mapping=_mapping_4519056720, target_language=%(language)s, default=_marker)"
            _result = _translate('button_add_factory', domain=_domain, mapping=_mapping_4519056720, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp3 = (_result is not _marker)
            if _tmp3:
                pass
                u'_result'
                _tmp4 = _result
                _write(_tmp4)
            else:
                pass
                u"_mapping_4519056720['typename']"
                _write(u'Add ')
                _tmp3 = _mapping_4519056720['typename']
                _write(_tmp3)
            _write(u'</a>')
            if (_tmp2 == 0):
                break
            _write(' ')
        _write(u'\n</div>')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/Euphorie/euphorie/deployment/tiles/templates/addbar.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
