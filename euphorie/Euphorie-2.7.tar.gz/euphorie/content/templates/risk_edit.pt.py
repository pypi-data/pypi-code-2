registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _attrs_4515572304 = _loads('(dp1\nVclass\np2\nVdiscrete\np3\ns.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4515573264 = _loads('(dp1\n.')
    _attrs_4515572496 = _loads('(dp1\n.')
    _attrs_4515573008 = _loads('(dp1\n.')
    _attrs_4515544016 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4515573456 = _loads('(dp1\n.')
    _attrs_4515598416 = _loads('(dp1\n.')
    _attrs_4515598608 = _loads('(dp1\nVtype\np2\nVsubmit\np3\nsVname\np4\nVform.buttons.cancel\np5\ns.')
    _attrs_4515571984 = _loads('(dp1\n.')
    _attrs_4515573200 = _loads('(dp1\n.')
    _attrs_4515572432 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4515572752 = _loads('(dp1\n.')
    _attrs_4515541968 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_4515572560 = _loads('(dp1\nVclass\np2\nVdiscrete\np3\ns.')
    _attrs_4515573136 = _loads('(dp1\n.')
    _attrs_4515573520 = _loads('(dp1\n.')
    _attrs_4515572048 = _loads('(dp1\nVclass\np2\nVbuttonBar\np3\ns.')
    _attrs_4515573712 = _loads('(dp1\nVtype\np2\nVsubmit\np3\nsVname\np4\nVform.buttons.save\np5\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4515572816 = _loads('(dp1\nVclass\np2\nVdiscrete\np3\ns.')
    _attrs_4515543440 = _loads('(dp1\n.')
    _attrs_4515573072 = _loads('(dp1\nVclass\np2\nVdiscrete\np3\ns.')
    _attrs_4515572688 = _loads('(dp1\n.')
    _attrs_4515571856 = _loads('(dp1\nVclass\np2\nVconcise\np3\nsVaction\np4\nV${request/getURL}\np5\nsVmethod\np6\nV${view/method}\np7\nsVenctype\np8\nV${view/enctype}\np9\ns.')
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
            u'context/aq_parent/title'
            _tmp1 = _path(econtext['context'], econtext['request'], True, 'aq_parent', 'title')
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
            _write(u'\n      ')
            attrs = _attrs_4515571856
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
            _write(u'>\n        ')
            attrs = _attrs_4515571984
            u"''"
            _write(u'<fieldset>\n          ')
            _default.value = default = ''
            'view/widgets/title/render'
            _content = _path(econtext['view'], econtext['request'], True, 'widgets', 'title', 'render')
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
            u"''"
            _write(u'\n          ')
            _default.value = default = ''
            'view/widgets/problem_description/render'
            _content = _path(econtext['view'], econtext['request'], True, 'widgets', 'problem_description', 'render')
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
            u"''"
            _write(u'\n          ')
            _default.value = default = ''
            'view/widgets/description/render'
            _content = _path(econtext['view'], econtext['request'], True, 'widgets', 'description', 'render')
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
            u"''"
            _write(u'\n          ')
            _default.value = default = ''
            'view/widgets/legal_reference/render'
            _content = _path(econtext['view'], econtext['request'], True, 'widgets', 'legal_reference', 'render')
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
            'view.groups[0]'
            _write(u'\n\n          ')
            group = _lookup_attr(econtext['view'], 'groups')[0]
            attrs = _attrs_4515541968
            _write(u'<fieldset>\n            ')
            _tmp_domain1 = _domain
            _tmp_domain1 = _domain
            u"'plone'"
            _domain = 'plone'
            'group/label'
            legend = _path(group, econtext['request'], True, 'label')
            'legend'
            _tmp1 = _path(legend, econtext['request'], True)
            if _tmp1:
                pass
                'legend'
                _content = _path(legend, econtext['request'], True)
                attrs = _attrs_4515544016
                u'_content'
                _write(u'<legend>')
                _tmp = _content
                u'%(translate)s(_tmp, domain=%(domain)s, mapping=None, target_language=%(language)s, default=None)'
                _tmp1 = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
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
                _write(u'</legend>')
            _write(u'\n            ')
            _domain = _tmp_domain1
            u"u'Group name'"
            _default.value = default = u'Group name'
            'group/description'
            description = _path(group, econtext['request'], True, 'description')
            'description'
            _tmp1 = _path(description, econtext['request'], True)
            if _tmp1:
                pass
                'description'
                _content = _path(description, econtext['request'], True)
                attrs = _attrs_4515572304
                u'_content'
                _write(u'<p class="discrete">')
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
            _write(u'\n            ')
            u"''"
            _default.value = default = ''
            'group/widgets/values'
            _tmp1 = _path(group, econtext['request'], True, 'widgets', 'values')
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
            _write(u'\n          </fieldset>\n          ')
            'view.groups[1]'
            group = _lookup_attr(econtext['view'], 'groups')[1]
            attrs = _attrs_4515543440
            _write(u'<fieldset>\n            ')
            _tmp_domain1 = _domain
            _tmp_domain1 = _domain
            u"'plone'"
            _domain = 'plone'
            'group/label'
            legend = _path(group, econtext['request'], True, 'label')
            'legend'
            _tmp1 = _path(legend, econtext['request'], True)
            if _tmp1:
                pass
                'legend'
                _content = _path(legend, econtext['request'], True)
                attrs = _attrs_4515572496
                u'_content'
                _write(u'<legend>')
                _tmp = _content
                u'%(translate)s(_tmp, domain=%(domain)s, mapping=None, target_language=%(language)s, default=None)'
                _tmp1 = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
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
                _write(u'</legend>')
            _write(u'\n            ')
            _domain = _tmp_domain1
            u"u'Group name'"
            _default.value = default = u'Group name'
            'group/description'
            description = _path(group, econtext['request'], True, 'description')
            'description'
            _tmp1 = _path(description, econtext['request'], True)
            if _tmp1:
                pass
                'description'
                _content = _path(description, econtext['request'], True)
                attrs = _attrs_4515572560
                u'_content'
                _write(u'<p class="discrete">')
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
            _write(u'\n            ')
            u"''"
            _default.value = default = ''
            'group/widgets/values'
            _tmp1 = _path(group, econtext['request'], True, 'widgets', 'values')
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
            _write(u'\n          </fieldset>\n          ')
            'view.groups[2]'
            group = _lookup_attr(econtext['view'], 'groups')[2]
            attrs = _attrs_4515572432
            _write(u'<fieldset>\n            ')
            _tmp_domain1 = _domain
            _tmp_domain1 = _domain
            u"'plone'"
            _domain = 'plone'
            'group/label'
            legend = _path(group, econtext['request'], True, 'label')
            'legend'
            _tmp1 = _path(legend, econtext['request'], True)
            if _tmp1:
                pass
                'legend'
                _content = _path(legend, econtext['request'], True)
                attrs = _attrs_4515572752
                u'_content'
                _write(u'<legend>')
                _tmp = _content
                u'%(translate)s(_tmp, domain=%(domain)s, mapping=None, target_language=%(language)s, default=None)'
                _tmp1 = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
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
                _write(u'</legend>')
            _write(u'\n            ')
            _domain = _tmp_domain1
            u"u'Group name'"
            _default.value = default = u'Group name'
            'group/description'
            description = _path(group, econtext['request'], True, 'description')
            'description'
            _tmp1 = _path(description, econtext['request'], True)
            if _tmp1:
                pass
                'description'
                _content = _path(description, econtext['request'], True)
                attrs = _attrs_4515572816
                u'_content'
                _write(u'<p class="discrete">')
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
            _write(u'\n            ')
            u"''"
            _default.value = default = ''
            'group/widgets/values'
            _tmp1 = _path(group, econtext['request'], True, 'widgets', 'values')
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
            _write(u'\n          </fieldset>\n          ')
            'view.groups[3]'
            group = _lookup_attr(econtext['view'], 'groups')[3]
            attrs = _attrs_4515572688
            _write(u'<fieldset>\n            ')
            _tmp_domain1 = _domain
            _tmp_domain1 = _domain
            u"'plone'"
            _domain = 'plone'
            'group/label'
            legend = _path(group, econtext['request'], True, 'label')
            'legend'
            _tmp1 = _path(legend, econtext['request'], True)
            if _tmp1:
                pass
                'legend'
                _content = _path(legend, econtext['request'], True)
                attrs = _attrs_4515573008
                u'_content'
                _write(u'<legend>')
                _tmp = _content
                u'%(translate)s(_tmp, domain=%(domain)s, mapping=None, target_language=%(language)s, default=None)'
                _tmp1 = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
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
                _write(u'</legend>')
            _write(u'\n            ')
            _domain = _tmp_domain1
            u"u'Group name'"
            _default.value = default = u'Group name'
            'group/description'
            description = _path(group, econtext['request'], True, 'description')
            'description'
            _tmp1 = _path(description, econtext['request'], True)
            if _tmp1:
                pass
                'description'
                _content = _path(description, econtext['request'], True)
                attrs = _attrs_4515573072
                u'_content'
                _write(u'<p class="discrete">')
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
            _write(u'\n\n            ')
            attrs = _attrs_4515573136
            _write(u'<fieldset>\n              ')
            attrs = _attrs_4515573264
            u"%(translate)s('header_secondary_images_1', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h5>')
            _result = _translate('header_secondary_images_1', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Secondary image 1')
            u"''"
            _write(u'</h5>\n              ')
            _default.value = default = ''
            'group/widgets/image2/render'
            _content = _path(group, econtext['request'], True, 'widgets', 'image2', 'render')
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
            u"''"
            _write(u'\n              ')
            _default.value = default = ''
            'group/widgets/caption2/render'
            _content = _path(group, econtext['request'], True, 'widgets', 'caption2', 'render')
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
            _write(u'\n            </fieldset>\n\n            ')
            attrs = _attrs_4515573200
            _write(u'<fieldset>\n              ')
            attrs = _attrs_4515573520
            u"%(translate)s('header_secondary_images_2', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h5>')
            _result = _translate('header_secondary_images_2', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Secondary image 2')
            u"''"
            _write(u'</h5>\n              ')
            _default.value = default = ''
            'group/widgets/image3/render'
            _content = _path(group, econtext['request'], True, 'widgets', 'image3', 'render')
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
            u"''"
            _write(u'\n              ')
            _default.value = default = ''
            'group/widgets/caption3/render'
            _content = _path(group, econtext['request'], True, 'widgets', 'caption3', 'render')
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
            _write(u'\n            </fieldset>\n\n            ')
            attrs = _attrs_4515573456
            _write(u'<fieldset>\n              ')
            attrs = _attrs_4515598416
            u"%(translate)s('header_secondary_images_3', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h5>')
            _result = _translate('header_secondary_images_3', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Secondary image 3')
            u"''"
            _write(u'</h5>\n              ')
            _default.value = default = ''
            'group/widgets/image4/render'
            _content = _path(group, econtext['request'], True, 'widgets', 'image4', 'render')
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
            u"''"
            _write(u'\n              ')
            _default.value = default = ''
            'group/widgets/caption4/render'
            _content = _path(group, econtext['request'], True, 'widgets', 'caption4', 'render')
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
            _write(u'\n            </fieldset>\n          </fieldset>\n        ')
            _write(u'</fieldset>\n\n        ')
            attrs = _attrs_4515572048
            _write(u'<div class="buttonBar">\n          ')
            attrs = _attrs_4515573712
            u"%(translate)s('button_save', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<button name="form.buttons.save" type="submit">')
            _result = _translate('button_save', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Save')
            _write(u'</button>\n          ')
            attrs = _attrs_4515598608
            u"%(translate)s('button_cancel', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<button name="form.buttons.cancel" type="submit">')
            _result = _translate('button_cancel', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Cancel')
            _write(u'</button>\n        </div>\n      </form>\n    \n')
        u"{'content': _callback_content, 'title': _callback_title}"
        _tmp = {'content': _callback_content, 'title': _callback_title, }
        'context/@@layout/macros/layout'
        _metal.render(_tmp, _out=_out, _write=_write, _domain=_domain, econtext=econtext)
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/Euphorie/euphorie/content/templates/risk_edit.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
