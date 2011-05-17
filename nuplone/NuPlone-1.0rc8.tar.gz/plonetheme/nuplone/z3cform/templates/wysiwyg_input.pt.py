registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4518051088 = _loads('(dp1\nVclass\np2\nVrich\np3\ns.')
    _attrs_4518050768 = _loads('(dp1\nVclass\np2\nV${view/@@dependencies}\np3\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4518050576 = _loads('(dp1\nVclass\np2\nVrichInput\np3\ns.')
    _attrs_4518050960 = _loads('(dp1\nVclass\np2\nVinfoPanel\np3\nsVtitle\np4\nVInformation\np5\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4518050896 = _loads('(dp1\nVclass\np2\nVrequired\np3\ns.')
    _attrs_4518051024 = _loads('(dp1\nVclass\np2\nVsuperImpose\np3\nsVfor\np4\nV${view/id}\np5\ns.')
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
        u"u'nuplone'"
        _domain = u'nuplone'
        _write(u'\n  ')
        attrs = _attrs_4518050576
        _write(u'<fieldset class="richInput">\n    ')
        attrs = _attrs_4518050768
        'join(value("_path(view, request, True, \'@@dependencies\')"),)'
        _write(u'<legend')
        _tmp1 = _path(econtext['view'], econtext['request'], True, '@@dependencies')
        if (_tmp1 is _default):
            _tmp1 = u'${view/@@dependencies}'
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = str(_tmp1)
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
            _write(((' class="' + _tmp1) + '"'))
        u'view/label'
        _write('>')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'label')
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
                _tmp = str(_tmp)
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
        u'view/required'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'required')
        if _tmp1:
            pass
            attrs = _attrs_4518050896
            _write(u'<sup class="required">*</sup>')
        u"''"
        _write(u'</legend> ')
        _default.value = default = ''
        u'view/field/description'
        description = _path(econtext['view'], econtext['request'], True, 'field', 'description')
        u'description'
        _tmp1 = _path(description, econtext['request'], True)
        if _tmp1:
            pass
            u'description'
            _content = _path(description, econtext['request'], True)
            attrs = _attrs_4518050960
            _write(u'<dfn class="infoPanel"')
            default = u'Information'
            u"%(translate)s(u'Information', domain=%(domain)s, mapping=None, target_language=%(language)s, default=None)"
            _tmp1 = _translate(u'Information', domain=_domain, mapping=None, target_language=target_language, default=None)
            default = None
            if (_tmp1 is _default):
                _tmp1 = u'Information'
            if ((_tmp1 is not None) and (_tmp1 is not False)):
                if (_tmp1.__class__ not in (str, unicode, int, float, )):
                    _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
                else:
                    if not isinstance(_tmp1, unicode):
                        _tmp1 = str(_tmp1)
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
                _write(((' title="' + _tmp1) + '"'))
            u'_content'
            _write('>')
            _tmp1 = _content
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
                    _tmp = str(_tmp)
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
            _write(u'</dfn>')
        _write(u'\n    ')
        attrs = _attrs_4518051024
        'join(value("_path(view, request, True, \'id\')"),)'
        _write(u'<label')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'id')
        if (_tmp1 is _default):
            _tmp1 = u'${view/id}'
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = str(_tmp1)
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
            _write(((' for="' + _tmp1) + '"'))
        u"u'Please enter text here'"
        _write(u' class="superImpose">')
        _msgid = u'Please enter text here'
        u"%(translate)s(' '.join(%(msgid)s.split()), domain=%(domain)s, mapping=None, target_language=%(language)s, default=%(msgid)s)"
        _result = _translate(_lookup_attr(' ', 'join')(_msgid.split()), domain=_domain, mapping=None, target_language=target_language, default=_msgid)
        u'_result'
        _tmp1 = _result
        _write((_tmp1 + u'</label>\n    '))
        attrs = _attrs_4518051088
        u'view/id'
        _write(u'<textarea class="rich"')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'id')
        if (_tmp1 is _default):
            _tmp1 = None
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = str(_tmp1)
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
            _write(((' id="' + _tmp1) + '"'))
        u'view/name'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'name')
        if (_tmp1 is _default):
            _tmp1 = None
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = str(_tmp1)
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
            _write(((' name="' + _tmp1) + '"'))
        u'view/disabled'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'disabled')
        if (_tmp1 is _default):
            _tmp1 = None
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = str(_tmp1)
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
            _write(((' disabled="' + _tmp1) + '"'))
        u'view/readonly'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'readonly')
        if (_tmp1 is _default):
            _tmp1 = None
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = str(_tmp1)
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
            _write(((' readonly="' + _tmp1) + '"'))
        u'view/cols'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'cols')
        if (_tmp1 is _default):
            _tmp1 = None
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = str(_tmp1)
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
            _write(((' cols="' + _tmp1) + '"'))
        u'view/rows'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'rows')
        if (_tmp1 is _default):
            _tmp1 = None
        if ((_tmp1 is not None) and (_tmp1 is not False)):
            if (_tmp1.__class__ not in (str, unicode, int, float, )):
                _tmp1 = unicode(_translate(_tmp1, domain=_domain, mapping=None, target_language=target_language, default=None))
            else:
                if not isinstance(_tmp1, unicode):
                    _tmp1 = str(_tmp1)
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
            _write(((' rows="' + _tmp1) + '"'))
        u"''"
        _write('>')
        _default.value = default = ''
        u'view/value'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'value')
        if _tmp1:
            pass
            u'view/value'
            _content = _path(econtext['view'], econtext['request'], True, 'value')
            u'_content'
            _tmp1 = _content
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
                    _tmp = str(_tmp)
                _write(_tmp)
        u"''"
        _write(u'</textarea> ')
        _default.value = default = ''
        u'view/error'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'error')
        if _tmp1:
            pass
            try:
                u'view/error/render'
                _content = _path(econtext['view'], econtext['request'], True, 'error', 'render')
            except Exception, e:
                u'nothing'
                _content = None
            
            u'_content'
            _tmp1 = _content
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
                    _tmp = str(_tmp)
                _write(_tmp)
        _write(u'\n  </fieldset>\n')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/z3cform/templates/wysiwyg_input.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
