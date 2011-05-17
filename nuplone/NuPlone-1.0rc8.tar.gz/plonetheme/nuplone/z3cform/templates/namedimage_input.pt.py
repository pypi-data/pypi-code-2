registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4519087184 = _loads('(dp1\nVname\np2\nV${view/name}.action\np3\nsVtype\np4\nVcheckbox\np5\nsVvalue\np6\nVremove\np7\ns.')
    _attrs_4519087824 = _loads('(dp1\nVname\np2\nV${view/name}\np3\nsVid\np4\nV${view/id}\np5\nsVdisabled\np6\nV${view/disabled}\np7\nsVreadonly\np8\nV${view/readonly}\np9\nsVtype\np10\nVfile\np11\nsVclass\np12\nV${view/klass}\np13\ns.')
    _attrs_4519088080 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4519086992 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\nsVclass\np4\nVcomprehensive ${view/@@dependencies}\np5\ns.')
    _attrs_4519087632 = _loads('(dp1\nVclass\np2\nVinfoPanel\np3\nsVtitle\np4\nVInformation\np5\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4519088016 = _loads('(dp1\nVsrc\np2\nV${scale/url}\np3\nsVwidth\np4\nV${scale/width}\np5\nsValt\np6\nV\nsVclass\np7\nVfloatAfter\np8\ns.')
    _attrs_4519087696 = _loads('(dp1\nVclass\np2\nVrequired\np3\ns.')
    _attrs_4519087376 = _loads('(dp1\n.')
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
        u'view/download_url'
        download_url = _path(econtext['view'], econtext['request'], True, 'download_url')
        attrs = _attrs_4519086992
        'join(u\'comprehensive \', value("_path(view, request, True, \'@@dependencies\')"))'
        _write(u'<fieldset xmlns="http://www.w3.org/1999/xhtml"')
        _tmp1 = ('%s%s' % (u'comprehensive ', _path(econtext['view'], econtext['request'], True, '@@dependencies'), ))
        if (_tmp1 is _default):
            _tmp1 = u'comprehensive ${view/@@dependencies}'
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
        _write(u'>\n  ')
        attrs = _attrs_4519087376
        u'view/label'
        _write(u'<legend>')
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
            attrs = _attrs_4519087696
            _write(u'<sup class="required">*</sup>')
        u'view/field/description'
        _write(u'</legend>\n  ')
        description = _path(econtext['view'], econtext['request'], True, 'field', 'description')
        u'description'
        _tmp1 = _path(description, econtext['request'], True)
        if _tmp1:
            pass
            attrs = _attrs_4519087632
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
            u'description'
            _write('>')
            _tmp1 = _path(description, econtext['request'], True)
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
        _write(u'\n  ')
        u'view/allow_nochange'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'allow_nochange')
        if _tmp1:
            pass
            u'context/@@images'
            _write('')
            images = _path(econtext['context'], econtext['request'], True, '@@images')
            u"images.scale(view.field.getName(), height=64, width=64, direction='thumbnail')"
            scale = _lookup_attr(images, 'scale')(_lookup_attr(_lookup_attr(econtext['view'], 'field'), 'getName')(), height=64, width=64, direction='thumbnail')
            u'scale'
            _tmp1 = _path(scale, econtext['request'], True)
            if _tmp1:
                pass
                attrs = _attrs_4519088016
                'join(value("_path(scale, request, True, \'url\')"),)'
                _write(u'<img class="floatAfter"')
                _tmp1 = _path(scale, econtext['request'], True, 'url')
                if (_tmp1 is _default):
                    _tmp1 = u'${scale/url}'
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
                    _write(((' src="' + _tmp1) + '"'))
                'join(value("_path(scale, request, True, \'width\')"),)'
                _tmp1 = _path(scale, econtext['request'], True, 'width')
                if (_tmp1 is _default):
                    _tmp1 = u'${scale/width}'
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
                    _write(((' width="' + _tmp1) + '"'))
                _write(u' alt="" />')
            _write(u'\n    ')
            attrs = _attrs_4519088080
            _write(u'<label>')
            attrs = _attrs_4519087184
            'join(value("_path(view, request, True, \'name\')"), u\'.action\')'
            _write(u'<input type="checkbox"')
            _tmp1 = ('%s%s' % (_path(econtext['view'], econtext['request'], True, 'name'), u'.action', ))
            if (_tmp1 is _default):
                _tmp1 = u'${view/name}.action'
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
            u"u'Remove image'"
            _write(u' value="remove" /> ')
            _msgid = u'Remove image'
            u"%(translate)s(' '.join(%(msgid)s.split()), domain=%(domain)s, mapping=None, target_language=%(language)s, default=%(msgid)s)"
            _result = _translate(_lookup_attr(' ', 'join')(_msgid.split()), domain=_domain, mapping=None, target_language=target_language, default=_msgid)
            u'_result'
            _tmp1 = _result
            _write((_tmp1 + u'</label>'))
        _write(u'\n  ')
        attrs = _attrs_4519087824
        'join(value("_path(view, request, True, \'id\')"),)'
        _write(u'<input type="file"')
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
            _write(((' id="' + _tmp1) + '"'))
        'join(value("_path(view, request, True, \'name\')"),)'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'name')
        if (_tmp1 is _default):
            _tmp1 = u'${view/name}'
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
        'join(value("_path(view, request, True, \'klass\')"),)'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'klass')
        if (_tmp1 is _default):
            _tmp1 = u'${view/klass}'
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
        'join(value("_path(view, request, True, \'disabled\')"),)'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'disabled')
        if (_tmp1 is _default):
            _tmp1 = u'${view/disabled}'
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
        'join(value("_path(view, request, True, \'readonly\')"),)'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'readonly')
        if (_tmp1 is _default):
            _tmp1 = u'${view/readonly}'
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
        u"''"
        _write(u' /> ')
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
        _write(u'\n</fieldset>')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/z3cform/templates/namedimage_input.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
