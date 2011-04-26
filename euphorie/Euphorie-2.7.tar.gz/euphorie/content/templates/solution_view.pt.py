registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4405071824 = _loads('(dp1\n.')
    _attrs_4405068176 = _loads('(dp1\nVclass\np2\nVgrid span-9\np3\ns.')
    _attrs_4405071760 = _loads('(dp1\n.')
    _lookup_tile = _loads('cplonetheme.nuplone.tiles.tales\n_lookup_tile\np1\n.')
    _attrs_4405070800 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4513463632 = _loads('(dp1\n.')
    _attrs_4405068880 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4405070224 = _loads('(dp1\n.')
    _attrs_4405068752 = _loads('(dp1\n.')
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
        _write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        _tmp_domain0 = _domain
        u"'euphorie'"
        _domain = 'euphorie'
        'context/@@layout/macros/layout'
        _metal = _path(econtext['context'], econtext['request'], True, '@@layout', 'macros', 'layout')
        def _callback_title(econtext, _repeat, _out=_out, _write=_write, _domain=_domain, **_ignored):
            if _repeat:
                repeat.update(_repeat)
            u"u'Standard solution'"
            _msgid = u'Standard solution'
            u"%(translate)s(' '.join(%(msgid)s.split()), domain=%(domain)s, mapping=None, target_language=%(language)s, default=%(msgid)s)"
            _result = _translate(_lookup_attr(' ', 'join')(_msgid.split()), domain=_domain, mapping=None, target_language=target_language, default=_msgid)
            u'_result'
            _tmp1 = _result
            _write((_tmp1 + '\n'))
        def _callback_buttonbar(econtext, _repeat, _out=_out, _write=_write, _domain=_domain, **_ignored):
            if _repeat:
                repeat.update(_repeat)
            u"''"
            _default.value = default = ''
            'euphorie.addbar'
            _content = _lookup_tile(econtext['context'], econtext['request'], 'euphorie.addbar')
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
            _write('\n')
        def _callback_content(econtext, _repeat, _out=_out, _write=_write, _domain=_domain, **_ignored):
            if _repeat:
                repeat.update(_repeat)
            "tools.checkPermission('Modify portal content')"
            can_edit = _lookup_attr(econtext['tools'], 'checkPermission')('Modify portal content')
            u"u'A description of the solution'"
            _write(u'\n      ')
            _default.value = default = u'A description of the solution'
            'context/description'
            _content = _path(econtext['context'], econtext['request'], True, 'description')
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
                    _tmp = unicode(str(_tmp), 'UTF-8')
                _write(_tmp)
            _write(u'\n\n      ')
            attrs = _attrs_4513463632
            u"%(translate)s('header_information', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h2>')
            _result = _translate('header_information', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Information')
            _write(u'</h2>\n\n      ')
            attrs = _attrs_4405068176
            _write(u'<dl class="grid span-9">\n        ')
            attrs = _attrs_4405068880
            u"%(translate)s('label_measure_action_plan', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<dt>')
            _result = _translate('label_measure_action_plan', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Action plan')
            _write(u'</dt>\n        ')
            attrs = _attrs_4405070224
            u'context/action_plan'
            _write(u'<dd>')
            _tmp1 = _path(econtext['context'], econtext['request'], True, 'action_plan')
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
            'context/prevention_plan'
            _write(u'</dd>\n        ')
            _tmp1 = _path(econtext['context'], econtext['request'], True, 'prevention_plan')
            if _tmp1:
                pass
                _write(u'\n          ')
                attrs = _attrs_4405068752
                u"%(translate)s('label_measure_prevention_plan', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<dt>')
                _result = _translate('label_measure_prevention_plan', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Prevention plan')
                _write(u'</dt>\n          ')
                attrs = _attrs_4405071824
                u'context/prevention_plan'
                _write(u'<dd>')
                _tmp1 = _path(econtext['context'], econtext['request'], True, 'prevention_plan')
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
                _write(u'</dd>\n        ')
            'context/requirements'
            _write(u'\n        ')
            _tmp1 = _path(econtext['context'], econtext['request'], True, 'requirements')
            if _tmp1:
                pass
                _write(u'\n          ')
                attrs = _attrs_4405070800
                u"%(translate)s('label_measure_requirements', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<dt>')
                _result = _translate('label_measure_requirements', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Requirements')
                _write(u'</dt>\n          ')
                attrs = _attrs_4405071760
                u'context/requirements'
                _write(u'<dd>')
                _tmp1 = _path(econtext['context'], econtext['request'], True, 'requirements')
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
                _write(u'</dd>\n        ')
            _write(u'\n      </dl>\n    ')
            _write('\n')
        u"{'content': _callback_content, 'buttonbar': _callback_buttonbar, 'title': _callback_title}"
        _tmp = {'content': _callback_content, 'buttonbar': _callback_buttonbar, 'title': _callback_title, }
        'context/@@layout/macros/layout'
        _metal.render(_tmp, _out=_out, _write=_write, _domain=_domain, econtext=econtext)
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/Euphorie/euphorie/content/templates/solution_view.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
