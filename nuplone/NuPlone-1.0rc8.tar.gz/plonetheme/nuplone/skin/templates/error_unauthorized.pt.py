registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4449259856 = _loads('(dp1\nVhref\np2\nV${tools/portal_url}/@@contact\np3\ns.')
    _attrs_4449259728 = _loads('(dp1\nVtype\np2\nVpassword\np3\nsVname\np4\nV__ac_password\np5\ns.')
    _attrs_4499599120 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _attrs_4449259984 = _loads('(dp1\nVhref\np2\nV${context/absolute_url}/@@request-password-reset\np3\ns.')
    _attrs_4499599056 = _loads('(dp1\nVname\np2\nVlogin_attempt\np3\nsVtype\np4\nVhidden\np5\nsVvalue\np6\nV1\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4453935376 = _loads('(dp1\nVclass\np2\nVmessage notice\np3\ns.')
    _attrs_4449259792 = _loads('(dp1\nVtype\np2\nVsubmit\np3\ns.')
    _attrs_4499598992 = _loads('(dp1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4449259600 = _loads('(dp1\n.')
    _attrs_4499598864 = _loads('(dp1\n.')
    _attrs_4499598736 = _loads('(dp1\nVaction\np2\nV${tools/portal_url}/@@login\np3\nsVclass\np4\nVconcise\np5\nsVmethod\np6\nVpost\np7\ns.')
    _attrs_4499599184 = _loads('(dp1\n.')
    _attrs_4499598800 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4499598672 = _loads('(dp1\nVclass\np2\nVmessage notice\np3\ns.')
    _attrs_4499599312 = _loads('(dp1\nVtype\np2\nVtext\np3\nsVname\np4\nV__ac_name\np5\ns.')
    _attrs_4499598928 = _loads('(dp1\nVclass\np2\nVbuttonBar\np3\ns.')
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
        'context/@@tools'
        tools = _path(econtext['context'], econtext['request'], True, '@@tools')
        'context/@@layout/macros/layout'
        _metal = _path(econtext['context'], econtext['request'], True, '@@layout', 'macros', 'layout')
        def _callback_title(econtext, _repeat, _out=_out, _domain=_domain, _write=_write, tools=tools, **_ignored):
            if _repeat:
                repeat.update(_repeat)
            'tools/anonymous'
            _write(u'')
            _tmp1 = _path(tools, econtext['request'], True, 'anonymous')
            if _tmp1:
                pass
                u"%(translate)s('header_login', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _result = _translate('header_login', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Login')
            u"not(_path(tools, request, True, 'anonymous'))"
            _tmp1 = not _path(tools, econtext['request'], True, 'anonymous')
            if _tmp1:
                pass
                u"%(translate)s('header_error_unauthorized', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _result = _translate('header_error_unauthorized', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Unauthorized')
            _write(u'\n')
        def _callback_content(econtext, _repeat, _out=_out, _domain=_domain, _write=_write, tools=tools, **_ignored):
            if _repeat:
                repeat.update(_repeat)
            u"not(_path(tools, request, True, 'anonymous'))"
            _write(u'\n      ')
            _tmp1 = not _path(tools, econtext['request'], True, 'anonymous')
            if _tmp1:
                pass
                attrs = _attrs_4453935376
                u"%(translate)s('message_error_unauthorized', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<p class="message notice">')
                _result = _translate('message_error_unauthorized', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'\n        I am afraid you are not authorised to do this.\n      ')
                _write(u'</p>')
            'tools/anonymous'
            _write(u'\n\n      ')
            _tmp1 = _path(tools, econtext['request'], True, 'anonymous')
            if _tmp1:
                pass
                _write(u'\n        ')
                attrs = _attrs_4499598672
                u"%(translate)s('message_error_not_logged_in', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<p class="message notice">')
                _result = _translate('message_error_not_logged_in', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'\n          You need to be logged in to access this page.\n        ')
                _write(u'</p>\n\n        ')
                attrs = _attrs_4499598736
                'join(value("_path(tools, request, True, \'portal_url\')"), u\'/@@login\')'
                _write(u'<form class="concise"')
                _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal_url'), '/@@login', ))
                if (_tmp1 is _default):
                    _tmp1 = u'${tools/portal_url}/@@login'
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
                _write(u' method="post">\n          ')
                attrs = _attrs_4499598864
                _write(u'<fieldset>\n            ')
                attrs = _attrs_4499598992
                u"%(translate)s('legend_credentials', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<legend>')
                _result = _translate('legend_credentials', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Credentials')
                _write(u'</legend>\n            ')
                attrs = _attrs_4499599056
                _write(u'<input type="hidden" name="login_attempt" value="1" />\n            ')
                attrs = _attrs_4499599120
                u"%(translate)s('label_login', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<label>')
                _result = _translate('label_login', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Login')
                _write(u'\n              ')
                attrs = _attrs_4499599312
                _write(u'<input name="__ac_name" type="text" /></label>\n            ')
                attrs = _attrs_4499599184
                u"%(translate)s('label_password', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<label>')
                _result = _translate('label_password', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Password')
                _write(u'\n              ')
                attrs = _attrs_4449259728
                _write(u'<input name="__ac_password" type="password" /></label>\n          </fieldset>\n\n          ')
                attrs = _attrs_4499598928
                _write(u'<div class="buttonBar">\n            ')
                attrs = _attrs_4449259792
                u"%(translate)s('button_login', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<button type="submit">')
                _result = _translate('button_login', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Login')
                _write(u'</button>\n          </div>\n        </form>\n\n        ')
                attrs = _attrs_4499598800
                u'{}'
                _write(u'<p>')
                _mapping_4499598800 = {}
                u'True'
                _tmp1 = True
                if _tmp1:
                    pass
                    _tmp_out3 = _out
                    _tmp_write3 = _write
                    u'_init_stream()'
                    (_out, _write, ) = _init_stream()
                    attrs = _attrs_4449259856
                    'join(value("_path(tools, request, True, \'portal_url\')"), u\'/@@contact\')'
                    _write(u'<a')
                    _tmp2 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal_url'), '/@@contact', ))
                    if (_tmp2 is _default):
                        _tmp2 = u'${tools/portal_url}/@@contact'
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
                    u"%(translate)s('message_no_account_request_account', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write('>')
                    _result = _translate('message_no_account_request_account', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp2 = (_result is not _marker)
                    if _tmp2:
                        pass
                        u'_result'
                        _tmp3 = _result
                        _write(_tmp3)
                    else:
                        pass
                        _write(u'request an account')
                    u'%(out)s.getvalue()'
                    _write(u'</a>')
                    _mapping_4499598800['request_account'] = _out.getvalue()
                    _write = _tmp_write3
                    _out = _tmp_out3
                u"%(translate)s('message_no_account', domain=%(domain)s, mapping=_mapping_4499598800, target_language=%(language)s, default=_marker)"
                _result = _translate('message_no_account', domain=_domain, mapping=_mapping_4499598800, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    u"_mapping_4499598800['request_account']"
                    _write(u'No account? Please ')
                    _tmp1 = _mapping_4499598800['request_account']
                    _write((_tmp1 + u'.'))
                _write(u'</p>\n      ')
                attrs = _attrs_4449259600
                u'{}'
                _write(u'<p>')
                _mapping_4449259600 = {}
                u'True'
                _tmp1 = True
                if _tmp1:
                    pass
                    _tmp_out3 = _out
                    _tmp_write3 = _write
                    u'_init_stream()'
                    (_out, _write, ) = _init_stream()
                    attrs = _attrs_4449259984
                    'join(value("_path(context, request, True, \'absolute_url\')"), u\'/@@request-password-reset\')'
                    _write(u'<a')
                    _tmp2 = ('%s%s' % (_path(econtext['context'], econtext['request'], True, 'absolute_url'), '/@@request-password-reset', ))
                    if (_tmp2 is _default):
                        _tmp2 = u'${context/absolute_url}/@@request-password-reset'
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
                    u"%(translate)s('reset_password', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write('>')
                    _result = _translate('reset_password', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp2 = (_result is not _marker)
                    if _tmp2:
                        pass
                        u'_result'
                        _tmp3 = _result
                        _write(_tmp3)
                    else:
                        pass
                        _write(u'request a password reset.')
                    u'%(out)s.getvalue()'
                    _write(u'</a>')
                    _mapping_4449259600['reset_password'] = _out.getvalue()
                    _write = _tmp_write3
                    _out = _tmp_out3
                u"%(translate)s('message_reset_password', domain=%(domain)s, mapping=_mapping_4449259600, target_language=%(language)s, default=_marker)"
                _result = _translate('message_reset_password', domain=_domain, mapping=_mapping_4449259600, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    u"_mapping_4449259600['reset_password']"
                    _write(u'If you forgot your password you can ')
                    _tmp1 = _mapping_4449259600['reset_password']
                    _write(_tmp1)
                _write(u'</p>\n      ')
            _write(u'\n')
        u"{'content': _callback_content, 'title': _callback_title}"
        _tmp = {'content': _callback_content, 'title': _callback_title, }
        'context/@@layout/macros/layout'
        _metal.render(_tmp, _out=_out, econtext=econtext, _domain=_domain, _write=_write, tools=tools)
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/skin/templates/error_unauthorized.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
