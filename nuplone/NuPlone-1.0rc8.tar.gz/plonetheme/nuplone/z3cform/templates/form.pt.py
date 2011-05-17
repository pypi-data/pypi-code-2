registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _attrs_4461933072 = _loads('(dp1\nVclass\np2\nV${group/layout|nothing}\np3\ns.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4461933200 = _loads('(dp1\n.')
    _attrs_4461932688 = _loads('(dp1\nVclass\np2\nVconcise\np3\nsVid\np4\nV${view/id}\np5\nsVaction\np6\nV${request/getURL}\np7\nsVmethod\np8\nV${view/method}\np9\nsVenctype\np10\nV${view/enctype}\np11\ns.')
    _attrs_4461875152 = _loads("(dp1\nVclass\np2\nVmessage ${python:'error' if view.widgets.errors else 'notice'}\np3\ns.")
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4483865744 = _loads('(dp1\nVclass\np2\nVbuttonBar\np3\ns.')
    _attrs_4461932816 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4461933264 = _loads('(dp1\nVclass\np2\nVdiscrete\np3\ns.')
    _attrs_4461932624 = _loads('(dp1\nVclass\np2\nVdiscrete\np3\ns.')
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
        u"'nuplone'"
        _domain = 'nuplone'
        'context/@@layout/macros/layout'
        _metal = _path(econtext['context'], econtext['request'], True, '@@layout', 'macros', 'layout')
        def _callback_title(econtext, _repeat, _out=_out, _write=_write, _domain=_domain, **_ignored):
            if _repeat:
                repeat.update(_repeat)
            u'view/label'
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
            u"u'Form-global message'"
            _write(u'\n    ')
            _default.value = default = u'Form-global message'
            _tmp_domain1 = _domain
            _tmp_domain1 = _domain
            u"'plone'"
            _domain = 'plone'
            'view/status'
            status = _path(econtext['view'], econtext['request'], True, 'status')
            'status'
            _tmp1 = _path(status, econtext['request'], True)
            if _tmp1:
                pass
                'status'
                _content = _path(status, econtext['request'], True)
                attrs = _attrs_4461875152
                'join(u\'message \', value("\'error\' if view.widgets.errors else \'notice\'"))'
                _write(u'<p')
                _tmp1 = ('%s%s' % ('message ', ('error' if _lookup_attr(_lookup_attr(econtext['view'], 'widgets'), 'errors') else 'notice'), ))
                if (_tmp1 is _default):
                    _tmp1 = u"message ${python:'error' if view.widgets.errors else 'notice'}"
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
                    _write(((' class="' + _tmp1) + '"'))
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
                _write(u'</p>')
            _write(u'\n    ')
            _domain = _tmp_domain1
            "getattr(view, 'description', None)"
            _tmp1 = getattr(econtext['view'], 'description', None)
            if _tmp1:
                pass
                attrs = _attrs_4461932624
                u'view/description'
                _write(u'<p class="discrete">')
                _tmp1 = _path(econtext['view'], econtext['request'], True, 'description')
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
                _write(u'</p>')
            _write(u'\n\n    ')
            attrs = _attrs_4461932688
            'join(value("_path(request, request, True, \'getURL\')"),)'
            _write(u'<form class="concise"')
            _tmp1 = _path(econtext['request'], econtext['request'], True, 'getURL')
            if (_tmp1 is _default):
                _tmp1 = u'${request/getURL}'
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
            'join(value("_path(view, request, True, \'enctype\')"),)'
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'enctype')
            if (_tmp1 is _default):
                _tmp1 = u'${view/enctype}'
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
                _write(((' enctype="' + _tmp1) + '"'))
            'join(value("_path(view, request, True, \'method\')"),)'
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'method')
            if (_tmp1 is _default):
                _tmp1 = u'${view/method}'
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
                _write(((' method="' + _tmp1) + '"'))
            'join(value("_path(view, request, True, \'id\')"),)'
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'id')
            if (_tmp1 is _default):
                _tmp1 = u'${view/id}'
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
                _write(((' id="' + _tmp1) + '"'))
            _write(u'>\n      ')
            attrs = _attrs_4461932816
            u"''"
            _write(u'<fieldset>\n        ')
            _default.value = default = ''
            'view/widgets/values'
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'widgets', 'values')
            widget = None
            (_tmp1, _tmp2, ) = repeat.insert('widget', _tmp1)
            for widget in _tmp1:
                _tmp2 = (_tmp2 - 1)
                'widget/render'
                _content = _path(widget, econtext['request'], True, 'render')
                u'_content'
                _tmp3 = _content
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
                    _write(_tmp)
                if (_tmp2 == 0):
                    break
                _write(' ')
            "getattr(view, 'groups', None)"
            _write(u'\n      </fieldset>\n\n      ')
            _tmp1 = getattr(econtext['view'], 'groups', None)
            if _tmp1:
                pass
                'view/groups'
                _write(u'\n        ')
                _tmp1 = _path(econtext['view'], econtext['request'], True, 'groups')
                group = None
                (_tmp1, _tmp2, ) = repeat.insert('group', _tmp1)
                for group in _tmp1:
                    _tmp2 = (_tmp2 - 1)
                    attrs = _attrs_4461933072
                    'join(parts(value("_path(group, request, True, \'layout\')"), value(\'None\')),)'
                    _write(u'<fieldset')
                    try:
                        u'group/layout'
                        _tmp5 = _path(group, econtext['request'], True, 'layout')
                    except Exception, e:
                        u'nothing'
                        _tmp5 = None
                    
                    _tmp3 = _tmp5
                    if (_tmp3 is _default):
                        _tmp3 = u'${group/layout|nothing}'
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
                    _write(u'>\n          ')
                    _tmp_domain3 = _domain
                    _tmp_domain3 = _domain
                    u"'plone'"
                    _domain = 'plone'
                    'group/label'
                    legend = _path(group, econtext['request'], True, 'label')
                    'legend'
                    _tmp3 = _path(legend, econtext['request'], True)
                    if _tmp3:
                        pass
                        attrs = _attrs_4461933200
                        _write(u'<legend>')
                        _tmp_out4 = _out
                        _tmp_write4 = _write
                        u'_init_stream()'
                        (_out, _write, ) = _init_stream()
                        u'legend'
                        _tmp3 = _path(legend, econtext['request'], True)
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
                        u'%(translate)s(%(out)s.getvalue(), domain=%(domain)s, mapping=None, target_language=%(language)s, default=None)'
                        _tmp = _translate(_out.getvalue(), domain=_domain, mapping=None, target_language=target_language, default=None)
                        _write = _tmp_write4
                        _out = _tmp_out4
                        u'_tmp'
                        _tmp3 = _tmp
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
                            _write(_tmp)
                        _write(u'</legend>')
                    _write(u'\n          ')
                    _domain = _tmp_domain3
                    'group/description'
                    description = _path(group, econtext['request'], True, 'description')
                    'description'
                    _tmp3 = _path(description, econtext['request'], True)
                    if _tmp3:
                        pass
                        attrs = _attrs_4461933264
                        u'description'
                        _write(u'<p class="discrete">')
                        _tmp3 = _path(description, econtext['request'], True)
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
                        _write(u'</p>')
                    _write(u'\n          ')
                    'group/widgets/values'
                    _tmp3 = _path(group, econtext['request'], True, 'widgets', 'values')
                    widget = None
                    (_tmp3, _tmp4, ) = repeat.insert('widget', _tmp3)
                    for widget in _tmp3:
                        _tmp4 = (_tmp4 - 1)
                        u"''"
                        _write(u'\n            ')
                        _default.value = default = ''
                        'widget/render'
                        _content = _path(widget, econtext['request'], True, 'render')
                        u'_content'
                        _tmp5 = _content
                        _tmp = _tmp5
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
                        _write(u'')
                        if (_tmp4 == 0):
                            break
                        _write(' ')
                    _write(u'\n        </fieldset>')
                    if (_tmp2 == 0):
                        break
                    _write(' ')
                _write(u'\n      ')
            _write(u'\n\n      ')
            try:
                'view/actions/values'
                actions = _path(econtext['view'], econtext['request'], True, 'actions', 'values')
            except Exception, e:
                'nothing'
                actions = None
            
            'actions'
            _tmp1 = _path(actions, econtext['request'], True)
            if _tmp1:
                pass
                attrs = _attrs_4483865744
                u"''"
                _write(u'<div class="buttonBar">\n        ')
                _default.value = default = ''
                'actions'
                _tmp1 = _path(actions, econtext['request'], True)
                action = None
                (_tmp1, _tmp2, ) = repeat.insert('action', _tmp1)
                for action in _tmp1:
                    _tmp2 = (_tmp2 - 1)
                    'action/render'
                    _content = _path(action, econtext['request'], True, 'render')
                    u'_content'
                    _tmp3 = _content
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
                        _write(_tmp)
                    if (_tmp2 == 0):
                        break
                    _write(' ')
                _write(u'\n      </div>')
            _write(u'\n    ')
            _write(u'</form>\n  \n')
        u"{'content': _callback_content, 'title': _callback_title}"
        _tmp = {'content': _callback_content, 'title': _callback_title, }
        'context/@@layout/macros/layout'
        _metal.render(_tmp, _out=_out, _write=_write, _domain=_domain, econtext=econtext)
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/z3cform/templates/form.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
