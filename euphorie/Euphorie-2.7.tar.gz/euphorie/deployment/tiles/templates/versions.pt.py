registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _attrs_4464497360 = _loads('(dp1\nVclass\np2\nVsample current published\np3\ns.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4501240016 = _loads('(dp1\nVclass\np2\nVlegend\np3\ns.')
    _attrs_4501238096 = _loads('(dp1\nVstyle\np2\nVdisplay: none\np3\nsVclass\np4\nVsurveyRevisions\np5\ns.')
    _attrs_4449547472 = _loads('(dp1\nVname\np2\nVaction\np3\nsVtitle\np4\nVCreate a duplicate of the selected survey\np5\nsVvalue\np6\nVclone\np7\nsVtype\np8\nVsubmit\np9\nsVclass\np10\nVmicro dependsOn-survey dependsAction-enable\np11\ns.')
    _attrs_4464439376 = _loads('(dp1\n.')
    _attrs_4465602960 = _loads('(dp1\nVhref\np2\nV${survey/url}/@@preview\np3\nsVclass\np4\nVfloatAfter\np5\ns.')
    _attrs_4501240144 = _loads('(dp1\nVclass\np2\nVpublished\np3\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4464442704 = _loads('(dp1\nVclass\np2\nVheaderButtons\np3\ns.')
    _attrs_4464442384 = _loads('(dp1\nVclass\np2\nVportletContent\np3\ns.')
    _attrs_4501238032 = _loads('(dp1\n.')
    _attrs_4464442512 = _loads('(dp1\nVclass\np2\nVradioList surveyVersions\np3\ns.')
    _attrs_4449547088 = _loads('(dp1\nVhref\np2\nV${survey/url}\np3\nsVclass\np4\nVfloatAfter\np5\ns.')
    _attrs_4464500112 = _loads("(dp1\nVname\np2\nVaction\np3\nsVtitle\np4\nVRemove this survey from the online client.\np5\nsVvalue\np6\nVunpublish\np7\nsVdisabled\np8\nV${python:'disabled' if not group.published else None}\np9\nsVtype\np10\nVsubmit\np11\nsVclass\np12\nVmicro\np13\ns.")
    _attrs_4464440912 = _loads('(dp1\nVclass\np2\nVversion\np3\ns.')
    _attrs_4449546640 = _loads('(dp1\nVhref\np2\nV${survey/url}/@@publish\np3\nsVclass\np4\nVbutton icon upload floatAfter\np5\ns.')
    _attrs_4518785104 = _loads('(dp1\nVclass\np2\nVsample published\np3\ns.')
    _attrs_4464441360 = _loads('(dp1\nVaction\np2\nV${view/action_url}\np3\ns.')
    _attrs_4501237840 = _loads('(dp1\n.')
    _attrs_4501240208 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4449502288 = _loads('(dp1\n.')
    _attrs_4464442192 = _loads('(dp1\nVclass\np2\nVlegend\np3\ns.')
    _attrs_4464440592 = _loads('(dp1\nVaction\np2\nV${group/url}/@@version-command\np3\nsVmethod\np4\nVpost\np5\ns.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_4449547152 = _loads('(dp1\nVhref\np2\nV${survey/url}\np3\ns.')
    _attrs_4464497488 = _loads("(dp1\nVchecked\np2\nV${python:'checked' if survey.published else None}\np3\nsVname\np4\nVsurvey\np5\nsVvalue\np6\nV${survey/id}\np7\nsVtype\np8\nVradio\np9\ns.")
    _attrs_4464441872 = _loads('(dp1\n.')
    _attrs_4501239568 = _loads('(dp1\nVclass\np2\nVbuttonBar top\np3\ns.')
    _attrs_4464497232 = _loads('(dp1\nVclass\np2\nVsample published\np3\ns.')
    _attrs_4464497104 = _loads('(dp1\nVclass\np2\nVsample current\np3\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4449546576 = _loads('(dp1\nVname\np2\nVaction\np3\nsVtitle\np4\nVPublish the selected survey live with its latest changes.\np5\nsVvalue\np6\nVpublish\np7\nsVdisabled\np8\nVdisabled\np9\nsVtype\np10\nVsubmit\np11\nsVclass\np12\nVmicro dependsOn-survey dependsAction-enable\np13\ns.')
    _attrs_4464442768 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\nsVid\np4\nVportletVersioning\np5\nsVclass\np6\nVportlet contextual\np7\ns.')
    _attrs_4518787024 = _loads('(dp1\nVclass\np2\nVbutton icon upload\np3\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _attrs_4501239440 = _loads('(dp1\nVname\np2\nVaction\np3\nsVtitle\np4\nVStart to write a new survey. You will be asked whether you want to start off with a copy of an existing survey.\np5\nsVvalue\np6\nVnew\np7\nsVtype\np8\nVsubmit\np9\nsVclass\np10\nVmicro\np11\ns.')
    _attrs_4518787344 = _loads('(dp1\nVclass\np2\nVsample current\np3\ns.')
    _attrs_4518786576 = _loads('(dp1\nVclass\np2\nVcurrent\np3\ns.')
    _attrs_4464500560 = _loads("(dp1\nVclass\np2\nV${python:' '.join(filter(None, ['current' if survey.current else None, 'published' if survey.published else None]))}\np3\ns.")
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
        'nocall:context/@@tools'
        tools = _path(econtext['context'], econtext['request'], False, '@@tools')
        'view.surveys'
        _tmp1 = _lookup_attr(econtext['view'], 'surveys')
        if _tmp1:
            pass
            attrs = _attrs_4464442768
            _write(u'<div xmlns="http://www.w3.org/1999/xhtml" id="portletVersioning" class="portlet contextual">\n  ')
            attrs = _attrs_4464439376
            u"%(translate)s('portlet_header_versions', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h3>')
            _result = _translate('portlet_header_versions', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Versions')
            _write(u'</h3>\n\n  ')
            attrs = _attrs_4464442384
            'view/surveys'
            _write(u'<div class="portletContent">\n    ')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'surveys')
            group = None
            (_tmp1, _tmp2, ) = repeat.insert('group', _tmp1)
            for group in _tmp1:
                _tmp2 = (_tmp2 - 1)
                attrs = _attrs_4464440592
                'join(value("_path(group, request, True, \'url\')"), u\'/@@version-command\')'
                _write(u'<form')
                _tmp3 = ('%s%s' % (_path(group, econtext['request'], True, 'url'), '/@@version-command', ))
                if (_tmp3 is _default):
                    _tmp3 = u'${group/url}/@@version-command'
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
                    _write(((' action="' + _tmp3) + '"'))
                _write(u' method="post">\n      ')
                attrs = _attrs_4464440912
                _write(u'<fieldset class="version">\n        ')
                attrs = _attrs_4464441872
                u'group/title'
                _write(u'<legend>')
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
                _write(u'</legend>\n\n        ')
                attrs = _attrs_4464442704
                _write(u'<fieldset class="headerButtons">\n          ')
                attrs = _attrs_4449547472
                _write(u'<button class="micro dependsOn-survey dependsAction-enable"')
                default = u'Create a duplicate of the selected survey'
                u'%(translate)s("help_add_version", domain=%(domain)s, mapping=None, target_language=%(language)s, default=u\'Create a duplicate of the selected survey\')'
                _tmp3 = _translate('help_add_version', domain=_domain, mapping=None, target_language=target_language, default=u'Create a duplicate of the selected survey')
                default = None
                if (_tmp3 is _default):
                    _tmp3 = u'Create a duplicate of the selected survey'
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
                u"%(translate)s('button_add_version', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u' type="submit" name="action" value="clone">')
                _result = _translate('button_add_version', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp3 = (_result is not _marker)
                if _tmp3:
                    pass
                    u'_result'
                    _tmp4 = _result
                    _write(_tmp4)
                else:
                    pass
                    _write(u'Duplicate')
                _write(u'</button>\n          ')
                attrs = _attrs_4449546576
                _write(u'<button class="micro dependsOn-survey dependsAction-enable"')
                default = u'Publish the selected survey live with its latest changes.'
                u'%(translate)s("help_publish", domain=%(domain)s, mapping=None, target_language=%(language)s, default=u\'Publish the selected survey live with its latest changes.\')'
                _tmp3 = _translate('help_publish', domain=_domain, mapping=None, target_language=target_language, default=u'Publish the selected survey live with its latest changes.')
                default = None
                if (_tmp3 is _default):
                    _tmp3 = u'Publish the selected survey live with its latest changes.'
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
                u"%(translate)s('button_publish', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u' disabled="disabled" type="submit" name="action" value="publish">')
                _result = _translate('button_publish', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp3 = (_result is not _marker)
                if _tmp3:
                    pass
                    u'_result'
                    _tmp4 = _result
                    _write(_tmp4)
                else:
                    pass
                    _write(u'Publish')
                _write(u'</button>\n          ')
                attrs = _attrs_4464500112
                _write(u'<button class="micro"')
                default = u'Remove this survey from the online client.'
                u'%(translate)s("title_help_unpublished", domain=%(domain)s, mapping=None, target_language=%(language)s, default=u\'Remove this survey from the online client.\')'
                _tmp3 = _translate('title_help_unpublished', domain=_domain, mapping=None, target_language=target_language, default=u'Remove this survey from the online client.')
                default = None
                if (_tmp3 is _default):
                    _tmp3 = u'Remove this survey from the online client.'
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
                'join(value("\'disabled\' if not group.published else None"),)'
                _tmp3 = ('disabled' if not _lookup_attr(group, 'published') else None)
                if (_tmp3 is _default):
                    _tmp3 = u"${python:'disabled' if not group.published else None}"
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
                    _write(((' disabled="' + _tmp3) + '"'))
                u"%(translate)s('button_unpublish', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u' type="submit" name="action" value="unpublish">')
                _result = _translate('button_unpublish', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp3 = (_result is not _marker)
                if _tmp3:
                    pass
                    u'_result'
                    _tmp4 = _result
                    _write(_tmp4)
                else:
                    pass
                    _write(u'Unpublish')
                _write(u'</button>\n        </fieldset>\n\n        ')
                attrs = _attrs_4464442512
                'group/surveys'
                _write(u'<ul class="radioList surveyVersions">\n          ')
                _tmp3 = _path(group, econtext['request'], True, 'surveys')
                survey = None
                (_tmp3, _tmp4, ) = repeat.insert('survey', _tmp3)
                for survey in _tmp3:
                    _tmp4 = (_tmp4 - 1)
                    attrs = _attrs_4464500560
                    'join(value("\' \'.join(filter(None, [\'current\' if survey.current else None, \'published\' if survey.published else None]))"),)'
                    _write(u'<li')
                    _tmp5 = _lookup_attr(' ', 'join')(filter(None, [('current' if _lookup_attr(survey, 'current') else None), ('published' if _lookup_attr(survey, 'published') else None), ]))
                    if (_tmp5 is _default):
                        _tmp5 = u"${python:' '.join(filter(None, ['current' if survey.current else None, 'published' if survey.published else None]))}"
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
                    'survey.current and not survey.published'
                    _write(u'>\n            ')
                    _tmp5 = (_lookup_attr(survey, 'current') and not _lookup_attr(survey, 'published'))
                    if _tmp5:
                        pass
                        attrs = _attrs_4464497104
                        u"%(translate)s('label_current', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                        _write(u'<em class="sample current">')
                        _result = _translate('label_current', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                        u'%(result)s is not %(marker)s'
                        _tmp5 = (_result is not _marker)
                        if _tmp5:
                            pass
                            u'_result'
                            _tmp6 = _result
                            _write(_tmp6)
                        else:
                            pass
                            _write(u'Current')
                        _write(u'</em>')
                    'not survey.current and survey.published'
                    _write(u'\n            ')
                    _tmp5 = (not _lookup_attr(survey, 'current') and _lookup_attr(survey, 'published'))
                    if _tmp5:
                        pass
                        attrs = _attrs_4464497232
                        u"%(translate)s('label_published', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                        _write(u'<em class="sample published">')
                        _result = _translate('label_published', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                        u'%(result)s is not %(marker)s'
                        _tmp5 = (_result is not _marker)
                        if _tmp5:
                            pass
                            u'_result'
                            _tmp6 = _result
                            _write(_tmp6)
                        else:
                            pass
                            _write(u'Published')
                        _write(u'</em>')
                    'survey.current and survey.published'
                    _write(u'\n            ')
                    _tmp5 = (_lookup_attr(survey, 'current') and _lookup_attr(survey, 'published'))
                    if _tmp5:
                        pass
                        attrs = _attrs_4464497360
                        u"%(translate)s('label_current_published', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                        _write(u'<em class="sample current published">')
                        _result = _translate('label_current_published', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                        u'%(result)s is not %(marker)s'
                        _tmp5 = (_result is not _marker)
                        if _tmp5:
                            pass
                            u'_result'
                            _tmp6 = _result
                            _write(_tmp6)
                        else:
                            pass
                            _write(u'Current / Published')
                        _write(u'</em>')
                    _write(u'\n            ')
                    attrs = _attrs_4464497488
                    'join(value("_path(survey, request, True, \'id\')"),)'
                    _write(u'<input type="radio" name="survey"')
                    _tmp5 = _path(survey, econtext['request'], True, 'id')
                    if (_tmp5 is _default):
                        _tmp5 = u'${survey/id}'
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
                        _write(((' value="' + _tmp5) + '"'))
                    'join(value("\'checked\' if survey.published else None"),)'
                    _tmp5 = ('checked' if _lookup_attr(survey, 'published') else None)
                    if (_tmp5 is _default):
                        _tmp5 = u"${python:'checked' if survey.published else None}"
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
                        _write(((' checked="' + _tmp5) + '"'))
                    _write(u' />\n            ')
                    attrs = _attrs_4449502288
                    _write(u'<label>')
                    attrs = _attrs_4449547152
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
                    _write(u'</a></label>\n            ')
                    attrs = _attrs_4465602960
                    'join(value("_path(survey, request, True, \'url\')"), u\'/@@preview\')'
                    _write(u'<a class="floatAfter"')
                    _tmp5 = ('%s%s' % (_path(survey, econtext['request'], True, 'url'), '/@@preview', ))
                    if (_tmp5 is _default):
                        _tmp5 = u'${survey/url}/@@preview'
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
                    u"%(translate)s('label_preview', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write('>')
                    _result = _translate('label_preview', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp5 = (_result is not _marker)
                    if _tmp5:
                        pass
                        u'_result'
                        _tmp6 = _result
                        _write(_tmp6)
                    else:
                        pass
                        _write(u'Preview')
                    _write(u'</a>\n            ')
                    attrs = _attrs_4449547088
                    'join(value("_path(survey, request, True, \'url\')"),)'
                    _write(u'<a class="floatAfter"')
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
                    u"%(translate)s('button_edit', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write('>')
                    _result = _translate('button_edit', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp5 = (_result is not _marker)
                    if _tmp5:
                        pass
                        u'_result'
                        _tmp6 = _result
                        _write(_tmp6)
                    else:
                        pass
                        _write(u'Edit')
                    'survey/modified'
                    _write(u'</a>\n            ')
                    _tmp5 = _path(survey, econtext['request'], True, 'modified')
                    if _tmp5:
                        pass
                        attrs = _attrs_4449546640
                        'join(value("_path(survey, request, True, \'url\')"), u\'/@@publish\')'
                        _write(u'<a class="button icon upload floatAfter"')
                        _tmp5 = ('%s%s' % (_path(survey, econtext['request'], True, 'url'), '/@@publish', ))
                        if (_tmp5 is _default):
                            _tmp5 = u'${survey/url}/@@publish'
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
                        u"%(translate)s('button_updated', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                        _write('>')
                        _result = _translate('button_updated', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                        u'%(result)s is not %(marker)s'
                        _tmp5 = (_result is not _marker)
                        if _tmp5:
                            pass
                            u'_result'
                            _tmp6 = _result
                            _write(_tmp6)
                        else:
                            pass
                            _write(u'Updated')
                        _write(u'</a>')
                    "survey['versions']"
                    _write(u'\n            ')
                    _tmp5 = survey['versions']
                    if _tmp5:
                        pass
                        attrs = _attrs_4501238096
                        'survey/versions'
                        _write(u'<ul class="surveyRevisions" style="display: none">\n              ')
                        _tmp5 = _path(survey, econtext['request'], True, 'versions')
                        version = None
                        (_tmp5, _tmp6, ) = repeat.insert('version', _tmp5)
                        for version in _tmp5:
                            _tmp6 = (_tmp6 - 1)
                            attrs = _attrs_4501237840
                            u'tools.formatDate(version["timestamp"])'
                            _write(u'<li>')
                            _tmp7 = _lookup_attr(tools, 'formatDate')(version['timestamp'])
                            _tmp = _tmp7
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
                            _write(u'\n              <!-- <a class="floatAfter" href="#" i18n:translate="button_view">View</a> --> </li>')
                            if (_tmp6 == 0):
                                break
                            _write(' ')
                        _write(u'\n            </ul>')
                    _write(u'\n          </li>')
                    if (_tmp4 == 0):
                        break
                    _write(' ')
                _write(u'\n        </ul>\n      </fieldset>\n    </form>')
                if (_tmp2 == 0):
                    break
                _write(' ')
            _write(u'\n\n    ')
            attrs = _attrs_4464441360
            'join(value("_path(view, request, True, \'action_url\')"),)'
            _write(u'<form')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'action_url')
            if (_tmp1 is _default):
                _tmp1 = u'${view/action_url}'
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
            _write(u'>\n      ')
            attrs = _attrs_4501239568
            _write(u'<p class="buttonBar top">\n        ')
            attrs = _attrs_4501239440
            _write(u'<button class="micro"')
            default = u'Start to write a new survey. You will be asked whether you want to start off with a copy of an existing survey.'
            u'%(translate)s("help_create_new_version", domain=%(domain)s, mapping=None, target_language=%(language)s, default=u\'Start to write a new survey. You will be asked whether you want to start off with a copy of an existing survey.\')'
            _tmp1 = _translate('help_create_new_version', domain=_domain, mapping=None, target_language=target_language, default=u'Start to write a new survey. You will be asked whether you want to start off with a copy of an existing survey.')
            default = None
            if (_tmp1 is _default):
                _tmp1 = u'Start to write a new survey. You will be asked whether you want to start off with a copy of an existing survey.'
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
                _write(((' title="' + _tmp1) + '"'))
            u"%(translate)s('button_create_new', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u' type="submit" name="action" value="new">')
            _result = _translate('button_create_new', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Create new survey')
            _write(u'</button>\n      </p>\n    </form>\n\n    ')
            attrs = _attrs_4464442192
            _write(u'<div class="legend">\n      ')
            attrs = _attrs_4501238032
            u"%(translate)s('header_legend', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<h5>')
            _result = _translate('header_legend', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Legend')
            _write(u'</h5>\n      ')
            attrs = _attrs_4501240016
            _write(u'<ul class="legend">\n        ')
            attrs = _attrs_4501240144
            u'{}'
            _write(u'<li class="published">')
            _mapping_4501240144 = {}
            u'True'
            _tmp1 = True
            if _tmp1:
                pass
                _tmp_out2 = _out
                _tmp_write2 = _write
                u'_init_stream()'
                (_out, _write, ) = _init_stream()
                attrs = _attrs_4518785104
                u"%(translate)s('label_published', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<em class="sample published">')
                _result = _translate('label_published', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp2 = (_result is not _marker)
                if _tmp2:
                    pass
                    u'_result'
                    _tmp3 = _result
                    _write(_tmp3)
                else:
                    pass
                    _write(u'Published')
                u'%(out)s.getvalue()'
                _write(u'</em>')
                _mapping_4501240144['label'] = _out.getvalue()
                _write = _tmp_write2
                _out = _tmp_out2
            u"%(translate)s('legend_published', domain=%(domain)s, mapping=_mapping_4501240144, target_language=%(language)s, default=_marker)"
            _result = _translate('legend_published', domain=_domain, mapping=_mapping_4501240144, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                u"_mapping_4501240144['label']"
                _tmp1 = _mapping_4501240144['label']
                _write((_tmp1 + u' Version that is currently online'))
            _write(u'</li>\n        ')
            attrs = _attrs_4518786576
            u'{}'
            _write(u'<li class="current">')
            _mapping_4518786576 = {}
            u'True'
            _tmp1 = True
            if _tmp1:
                pass
                _tmp_out2 = _out
                _tmp_write2 = _write
                u'_init_stream()'
                (_out, _write, ) = _init_stream()
                attrs = _attrs_4518787344
                u"%(translate)s('label_current', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<em class="sample current">')
                _result = _translate('label_current', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp2 = (_result is not _marker)
                if _tmp2:
                    pass
                    u'_result'
                    _tmp3 = _result
                    _write(_tmp3)
                else:
                    pass
                    _write(u'Current')
                u'%(out)s.getvalue()'
                _write(u'</em>')
                _mapping_4518786576['label'] = _out.getvalue()
                _write = _tmp_write2
                _out = _tmp_out2
            u"%(translate)s('legend_current', domain=%(domain)s, mapping=_mapping_4518786576, target_language=%(language)s, default=_marker)"
            _result = _translate('legend_current', domain=_domain, mapping=_mapping_4518786576, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                u"_mapping_4518786576['label']"
                _tmp1 = _mapping_4518786576['label']
                _write((_tmp1 + u' Version you are currently reviewing'))
            _write(u'</li>\n      </ul>\n      ')
            attrs = _attrs_4501240208
            u'{}'
            _write(u'<p>')
            _mapping_4501240208 = {}
            u'True'
            _tmp1 = True
            if _tmp1:
                pass
                _tmp_out2 = _out
                _tmp_write2 = _write
                u'_init_stream()'
                (_out, _write, ) = _init_stream()
                attrs = _attrs_4518787024
                u"%(translate)s('label_update', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<em class="button icon upload">')
                _result = _translate('label_update', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp2 = (_result is not _marker)
                if _tmp2:
                    pass
                    u'_result'
                    _tmp3 = _result
                    _write(_tmp3)
                else:
                    pass
                    _write(u'Update')
                u'%(out)s.getvalue()'
                _write(u'</em>')
                _mapping_4501240208['label'] = _out.getvalue()
                _write = _tmp_write2
                _out = _tmp_out2
            u"%(translate)s('legend_updated', domain=%(domain)s, mapping=_mapping_4501240208, target_language=%(language)s, default=_marker)"
            _result = _translate('legend_updated', domain=_domain, mapping=_mapping_4501240208, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                u"_mapping_4501240208['label']"
                _tmp1 = _mapping_4501240208['label']
                _write((_tmp1 + u' = This version has changes that are currently unpublished. Click the update icon to bring all the changes live'))
            _write(u'</p>\n    </div>\n  </div>\n</div>')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/Euphorie/euphorie/deployment/tiles/templates/versions.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
