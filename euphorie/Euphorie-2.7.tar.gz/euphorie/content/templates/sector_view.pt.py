registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4501671312 = _loads("(dp1\nVclass\np2\nV${python:'current' if survey.current else None}\np3\ns.")
    _attrs_4501757264 = _loads('(dp1\n.')
    _attrs_4501668240 = _loads('(dp1\nVhref\np2\nV#\ns.')
    _attrs_4501668816 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4501757776 = _loads('(dp1\n.')
    _attrs_4501754704 = _loads('(dp1\n.')
    _attrs_4463741520 = _loads('(dp1\nVclass\np2\nVsurveyVersions\np3\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4501668944 = _loads('(dp1\nVhref\np2\nV${survey/url}\np3\ns.')
    _attrs_4501757456 = _loads('(dp1\nVhref\np2\nV#\ns.')
    _attrs_4501757200 = _loads('(dp1\n.')
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
            u'context/title'
            _tmp1 = _path(econtext['context'], econtext['request'], True, 'title')
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
            attrs = _attrs_4501757200
            u"%(translate)s('header_sector_survey_list', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h2>')
            _result = _translate('header_sector_survey_list', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Surveys')
            'not view.surveys'
            _write(u'</h2>\n\n      ')
            _tmp1 = not _lookup_attr(econtext['view'], 'surveys')
            if _tmp1:
                pass
                attrs = _attrs_4501757264
                u'{}'
                _write(u'<p>')
                _mapping_4501757264 = {}
                u'True'
                _tmp1 = True
                if _tmp1:
                    pass
                    _tmp_out3 = _out
                    _tmp_write3 = _write
                    u'_init_stream()'
                    (_out, _write, ) = _init_stream()
                    attrs = _attrs_4501757456
                    'view/add_survey_url'
                    _write(u'<a')
                    _tmp2 = _path(econtext['view'], econtext['request'], True, 'add_survey_url')
                    if (_tmp2 is _default):
                        _tmp2 = u'#'
                    if ((_tmp2 is not None) and (_tmp2 is not False)):
                        if (_tmp2.__class__ not in (str, unicode, int, float, )):
                            _tmp2 = unicode(_translate(_tmp2, domain=_domain, mapping=None, target_language=target_language, default=None))
                        else:
                            if not isinstance(_tmp2, unicode):
                                _tmp2 = unicode(str(_tmp2), 'UTF-8')
                        if ('&' in _tmp2):
                            if (';' in _tmp2):
                                _tmp2 = _re_amp.sub('&amp;', _tmp2)
                            else:
                                _tmp2 = _tmp2.replace('&', '&amp;')
                        if ('<' in _tmp2):
                            _tmp2 = _tmp2.replace('<', '&lt;')
                        if ('>' in _tmp2):
                            _tmp2 = _tmp2.replace('>', '&gt;')
                        if ('"' in _tmp2):
                            _tmp2 = _tmp2.replace('"', '&quot;')
                        _write(((' href="' + _tmp2) + '"'))
                    u"%(translate)s('add_survey', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write('>')
                    _result = _translate('add_survey', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp2 = (_result is not _marker)
                    if _tmp2:
                        pass
                        u'_result'
                        _tmp3 = _result
                        _write(_tmp3)
                    else:
                        pass
                        _write(u'add\n        a new survey')
                    u'%(out)s.getvalue()'
                    _write(u'</a>')
                    _mapping_4501757264['add_link'] = _out.getvalue()
                    _write = _tmp_write3
                    _out = _tmp_out3
                u"%(translate)s('no_surveys_present', domain=%(domain)s, mapping=_mapping_4501757264, target_language=%(language)s, default=_marker)"
                _result = _translate('no_surveys_present', domain=_domain, mapping=_mapping_4501757264, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    u"_mapping_4501757264['add_link']"
                    _write(u'\n      There are no surveys present. You can ')
                    _tmp1 = _mapping_4501757264['add_link']
                    _write((_tmp1 + u'.\n      '))
                _write(u'</p>')
            'view/surveys'
            _write(u'\n\n      ')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'surveys')
            group = None
            (_tmp1, _tmp2, ) = repeat.insert('group', _tmp1)
            for group in _tmp1:
                _tmp2 = (_tmp2 - 1)
                _write(u'\n        ')
                attrs = _attrs_4501754704
                u'group/title'
                _write(u'<h5>')
                _tmp3 = _path(group, econtext['request'], True, 'title')
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
                'view.surveys'
                _write(u'</h5>\n        ')
                _tmp3 = _lookup_attr(econtext['view'], 'surveys')
                if _tmp3:
                    pass
                    attrs = _attrs_4463741520
                    'group/surveys'
                    _write(u'<ul class="surveyVersions">\n            ')
                    _tmp3 = _path(group, econtext['request'], True, 'surveys')
                    survey = None
                    (_tmp3, _tmp4, ) = repeat.insert('survey', _tmp3)
                    for survey in _tmp3:
                        _tmp4 = (_tmp4 - 1)
                        attrs = _attrs_4501671312
                        'join(value("\'current\' if survey.current else None"),)'
                        _write(u'<li')
                        _tmp5 = ('current' if _lookup_attr(survey, 'current') else None)
                        if (_tmp5 is _default):
                            _tmp5 = u"${python:'current' if survey.current else None}"
                        if ((_tmp5 is not None) and (_tmp5 is not False)):
                            if (_tmp5.__class__ not in (str, unicode, int, float, )):
                                _tmp5 = unicode(_translate(_tmp5, domain=_domain, mapping=None, target_language=target_language, default=None))
                            else:
                                if not isinstance(_tmp5, unicode):
                                    _tmp5 = unicode(str(_tmp5), 'UTF-8')
                            if ('&' in _tmp5):
                                if (';' in _tmp5):
                                    _tmp5 = _re_amp.sub('&amp;', _tmp5)
                                else:
                                    _tmp5 = _tmp5.replace('&', '&amp;')
                            if ('<' in _tmp5):
                                _tmp5 = _tmp5.replace('<', '&lt;')
                            if ('>' in _tmp5):
                                _tmp5 = _tmp5.replace('>', '&gt;')
                            if ('"' in _tmp5):
                                _tmp5 = _tmp5.replace('"', '&quot;')
                            _write(((' class="' + _tmp5) + '"'))
                        _write(u'>\n              ')
                        attrs = _attrs_4501668816
                        _write(u'<label>')
                        attrs = _attrs_4501668944
                        'join(value("_path(survey, request, True, \'url\')"),)'
                        _write(u'<a')
                        _tmp5 = _path(survey, econtext['request'], True, 'url')
                        if (_tmp5 is _default):
                            _tmp5 = u'${survey/url}'
                        if ((_tmp5 is not None) and (_tmp5 is not False)):
                            if (_tmp5.__class__ not in (str, unicode, int, float, )):
                                _tmp5 = unicode(_translate(_tmp5, domain=_domain, mapping=None, target_language=target_language, default=None))
                            else:
                                if not isinstance(_tmp5, unicode):
                                    _tmp5 = unicode(str(_tmp5), 'UTF-8')
                            if ('&' in _tmp5):
                                if (';' in _tmp5):
                                    _tmp5 = _re_amp.sub('&amp;', _tmp5)
                                else:
                                    _tmp5 = _tmp5.replace('&', '&amp;')
                            if ('<' in _tmp5):
                                _tmp5 = _tmp5.replace('<', '&lt;')
                            if ('>' in _tmp5):
                                _tmp5 = _tmp5.replace('>', '&gt;')
                            if ('"' in _tmp5):
                                _tmp5 = _tmp5.replace('"', '&quot;')
                            _write(((' href="' + _tmp5) + '"'))
                        u'survey/title'
                        _write('>')
                        _tmp5 = _path(survey, econtext['request'], True, 'title')
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
                        _write(u'</a></label>\n            </li>')
                        if (_tmp4 == 0):
                            break
                        _write(' ')
                    _write(u'\n        </ul>')
                _write(u'\n      ')
                if (_tmp2 == 0):
                    break
                _write(' ')
            'view.surveys'
            _write(u'\n\n      ')
            _tmp1 = _lookup_attr(econtext['view'], 'surveys')
            if _tmp1:
                pass
                attrs = _attrs_4501757776
                u'{}'
                _write(u'<p>')
                _mapping_4501757776 = {}
                u'True'
                _tmp1 = True
                if _tmp1:
                    pass
                    _tmp_out3 = _out
                    _tmp_write3 = _write
                    u'_init_stream()'
                    (_out, _write, ) = _init_stream()
                    attrs = _attrs_4501668240
                    'view/add_survey_url'
                    _write(u'<a')
                    _tmp2 = _path(econtext['view'], econtext['request'], True, 'add_survey_url')
                    if (_tmp2 is _default):
                        _tmp2 = u'#'
                    if ((_tmp2 is not None) and (_tmp2 is not False)):
                        if (_tmp2.__class__ not in (str, unicode, int, float, )):
                            _tmp2 = unicode(_translate(_tmp2, domain=_domain, mapping=None, target_language=target_language, default=None))
                        else:
                            if not isinstance(_tmp2, unicode):
                                _tmp2 = unicode(str(_tmp2), 'UTF-8')
                        if ('&' in _tmp2):
                            if (';' in _tmp2):
                                _tmp2 = _re_amp.sub('&amp;', _tmp2)
                            else:
                                _tmp2 = _tmp2.replace('&', '&amp;')
                        if ('<' in _tmp2):
                            _tmp2 = _tmp2.replace('<', '&lt;')
                        if ('>' in _tmp2):
                            _tmp2 = _tmp2.replace('>', '&gt;')
                        if ('"' in _tmp2):
                            _tmp2 = _tmp2.replace('"', '&quot;')
                        _write(((' href="' + _tmp2) + '"'))
                    u"%(translate)s('add_survey', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write('>')
                    _result = _translate('add_survey', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp2 = (_result is not _marker)
                    if _tmp2:
                        pass
                        u'_result'
                        _tmp3 = _result
                        _write(_tmp3)
                    else:
                        pass
                        _write(u'add\n        a new survey')
                    u'%(out)s.getvalue()'
                    _write(u'</a>')
                    _mapping_4501757776['add_link'] = _out.getvalue()
                    _write = _tmp_write3
                    _out = _tmp_out3
                u"%(translate)s('survey_list_footer', domain=%(domain)s, mapping=_mapping_4501757776, target_language=%(language)s, default=_marker)"
                _result = _translate('survey_list_footer', domain=_domain, mapping=_mapping_4501757776, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    u"_mapping_4501757776['add_link']"
                    _write(u'\n      You can also ')
                    _tmp1 = _mapping_4501757776['add_link']
                    _write((_tmp1 + u'.\n      '))
                _write(u'</p>')
            _write(u'\n    \n')
        u"{'content': _callback_content, 'title': _callback_title}"
        _tmp = {'content': _callback_content, 'title': _callback_title, }
        'context/@@layout/macros/layout'
        _metal.render(_tmp, _out=_out, _write=_write, _domain=_domain, econtext=econtext)
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/Euphorie/euphorie/content/templates/sector_view.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
