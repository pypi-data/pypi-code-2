registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _attrs_4464450576 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _attrs_4464450512 = _loads('(dp1\n.')
    _attrs_4464451536 = _loads('(dp1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4464452240 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _attrs_4464450896 = _loads('(dp1\nVtarget\np2\nV_parent\np3\ns.')
    _attrs_4464451856 = _loads('(dp1\nVhref\np2\nV${menu/url|string:#}\np3\nsVclass\np4\nVcontextActions\np5\ns.')
    _attrs_4464452048 = _loads('(dp1\nVhref\np2\nV${tools/portal_url}/@@logout\np3\ns.')
    _attrs_4464451664 = _loads('(dp1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_4464452688 = _loads('(dp1\nVhref\np2\nV${entry/url}\np3\nsVtitle\np4\nV${entry/description|nothing}\np5\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4464451280 = _loads('(dp1\nVhref\np2\nV${tools/navroot_url}/@@login?came_from=${request/environ/HTTP_REFERER|context/absolute_url}\np3\ns.')
    _attrs_4464452560 = _loads('(dp1\n.')
    _attrs_4464451728 = _loads('(dp1\n.')
    _attrs_4464450768 = _loads('(dp1\nVrel\np2\nVstylesheet\np3\nsVmedia\np4\nVall\np5\nsVtype\np6\nVtext/css\np7\ns.')
    _attrs_4464451344 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _attrs_4464450832 = _loads('(dp1\n.')
    _attrs_4464452496 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _checkPermission = _loads('cplonetheme.nuplone.utils\ncheckPermission\np1\n.')
    _attrs_4464452112 = _loads('(dp1\n.')
    _attrs_4464452176 = _loads('(dp1\nVhref\np2\nV${view/settings_url}\np3\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4464451984 = _loads('(dp1\n.')
    _attrs_4464451408 = _loads('(dp1\nVhref\np2\nV${view/settings_url}\np3\ns.')
    _attrs_4464452304 = _loads('(dp1\n.')
    _attrs_4464450704 = _loads('(dp1\nVclass\np2\nVsiteMenu\np3\ns.')
    _attrs_4464451472 = _loads('(dp1\n.')
    _attrs_4464451024 = _loads('(dp1\nVclass\np2\nVmenu\np3\nsVid\np4\nVsiteMenu\np5\ns.')
    _attrs_4464451920 = _loads('(dp1\n.')
    _attrs_4464451088 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _attrs_4464450320 = _loads('(dp1\nVcontent\np2\nVtext/html; charset=utf-8\np3\nsVhttp-equiv\np4\nVContent-Type\np5\ns.')
    _attrs_4464451792 = _loads('(dp1\n.')
    _attrs_4464452368 = _loads('(dp1\nVhref\np2\nV${context/absolute_url}/@@edit\np3\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4464452432 = _loads('(dp1\n.')
    _attrs_4464451152 = _loads('(dp1\nVid\np2\nVuser\np3\ns.')
    _attrs_4464451216 = _loads('(dp1\nVid\np2\nVuser\np3\ns.')
    _attrs_4464450256 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
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
        'context/@@tools'
        tools = _path(econtext['context'], econtext['request'], True, '@@tools')
        'view/factories'
        factories = _path(econtext['view'], econtext['request'], True, 'factories')
        attrs = _attrs_4464450256
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n  ')
        attrs = _attrs_4464450512
        _write(u'<head>\n    ')
        attrs = _attrs_4464450320
        _write(u'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n    ')
        attrs = _attrs_4464450576
        'tools/portal/++resource++NuPlone.libraries/css_browser_selector.js'
        _write(u'<script type="text/javascript"')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.libraries', 'css_browser_selector.js')
        if (_tmp1 is _default):
            _tmp1 = None
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
            _write(((' src="' + _tmp1) + '"'))
        _write(u'></script>\n    ')
        attrs = _attrs_4464450768
        '${tools/portal/++resource++NuPlone.style/main}/base.css'
        _write(u'<link rel="stylesheet" type="text/css" media="all"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.style', 'main'), '/base.css', ))
        if (_tmp1 is _default):
            _tmp1 = None
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
        _write(u' />\n    ')
        attrs = _attrs_4464450832
        u"%(translate)s('title_site_menu', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<title>')
        _result = _translate('title_site_menu', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Site menu')
        _write(u'</title>\n    ')
        attrs = _attrs_4464450896
        _write(u'<base target="_parent" />\n  </head>\n  ')
        attrs = _attrs_4464450704
        _write(u'<body class="siteMenu">\n    ')
        attrs = _attrs_4464451024
        'tools/anonymous'
        _write(u'<ul class="menu" id="siteMenu">\n      ')
        _tmp1 = _path(tools, econtext['request'], True, 'anonymous')
        if _tmp1:
            pass
            attrs = _attrs_4464451152
            _write(u'<li id="user">\n        ')
            attrs = _attrs_4464451280
            'join(value("_path(tools, request, True, \'navroot_url\')"), u\'/@@login?came_from=\', parts(value("_path(request, request, True, \'environ\', \'HTTP_REFERER\')"), value("_path(context, request, True, \'absolute_url\')")))'
            _write(u'<a')
            try:
                u'request/environ/HTTP_REFERER'
                _tmp3 = _path(econtext['request'], econtext['request'], True, 'environ', 'HTTP_REFERER')
            except Exception, e:
                u'context/absolute_url'
                _tmp3 = _path(econtext['context'], econtext['request'], True, 'absolute_url')
            
            _tmp1 = ('%s%s%s' % (_path(tools, econtext['request'], True, 'navroot_url'), '/@@login?came_from=', _tmp3, ))
            if (_tmp1 is _default):
                _tmp1 = u'${tools/navroot_url}/@@login?came_from=${request/environ/HTTP_REFERER|context/absolute_url}'
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
            u"%(translate)s('menu_login', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write('>')
            _result = _translate('menu_login', domain=_domain, mapping=None, target_language=target_language, default=_marker)
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
            _write(u'</a>\n      </li>')
        u"not(_path(tools, request, True, 'anonymous'))"
        _write(u'\n      ')
        _tmp1 = not _path(tools, econtext['request'], True, 'anonymous')
        if _tmp1:
            pass
            attrs = _attrs_4464451216
            _write(u'<li id="user">\n      ')
            attrs = _attrs_4464451408
            'join(value("_path(view, request, True, \'settings_url\')"),)'
            _write(u'<a')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'settings_url')
            if (_tmp1 is _default):
                _tmp1 = u'${view/settings_url}'
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
            u"tools.user.getProperty('fullname', '') or tools.user.getUserName()"
            _write('>')
            _tmp1 = (_lookup_attr(_lookup_attr(tools, 'user'), 'getProperty')('fullname', '') or _lookup_attr(_lookup_attr(tools, 'user'), 'getUserName')())
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
            _write(u'</a>\n        ')
            attrs = _attrs_4464451472
            _write(u'<ul>\n          ')
            attrs = _attrs_4464451664
            _write(u'<li>\n            ')
            attrs = _attrs_4464451792
            _write(u'<ul>\n              ')
            attrs = _attrs_4464451920
            _write(u'<li>\n                ')
            attrs = _attrs_4464452048
            'join(value("_path(tools, request, True, \'portal_url\')"), u\'/@@logout\')'
            _write(u'<a')
            _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal_url'), '/@@logout', ))
            if (_tmp1 is _default):
                _tmp1 = u'${tools/portal_url}/@@logout'
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
            u"%(translate)s('menu_logout', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write('>')
            _result = _translate('menu_logout', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Log out')
            _write(u'</a>\n              </li>\n              ')
            attrs = _attrs_4464451984
            _write(u'<li>\n                ')
            attrs = _attrs_4464452176
            'join(value("_path(view, request, True, \'settings_url\')"),)'
            _write(u'<a')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'settings_url')
            if (_tmp1 is _default):
                _tmp1 = u'${view/settings_url}'
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
            u"%(translate)s('menu_settings', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write('>')
            _result = _translate('menu_settings', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Settings')
            _write(u'</a>\n              </li>\n            </ul>\n          </li>\n        </ul>\n      </li>')
        "view.view_type=='view' and view.actions"
        _write(u'\n      ')
        _tmp1 = ((_lookup_attr(econtext['view'], 'view_type') == 'view') and _lookup_attr(econtext['view'], 'actions'))
        if _tmp1:
            pass
            'view/actions'
            _write(u'\n        ')
            menu = _path(econtext['view'], econtext['request'], True, 'actions')
            attrs = _attrs_4464451536
            _write(u'<li>\n          ')
            attrs = _attrs_4464451856
            'join(parts(value("_path(menu, request, True, \'url\')"), join(u\'#\',)),)'
            _write(u'<a class="contextActions"')
            try:
                u'menu/url'
                _tmp3 = _path(menu, econtext['request'], True, 'url')
            except Exception, e:
                u'#'
                _tmp3 = '#'
            
            _tmp1 = _tmp3
            if (_tmp1 is _default):
                _tmp1 = u'${menu/url|string:#}'
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
            u'menu/title'
            _write('>')
            _tmp1 = _path(menu, econtext['request'], True, 'title')
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
            _write(u'</a>\n          ')
            attrs = _attrs_4464452112
            'menu/children'
            _write(u'<ul>\n            ')
            _tmp1 = _path(menu, econtext['request'], True, 'children')
            submenu = None
            (_tmp1, _tmp2, ) = repeat.insert('submenu', _tmp1)
            for submenu in _tmp1:
                _tmp2 = (_tmp2 - 1)
                attrs = _attrs_4464452304
                u'submenu/title'
                _write(u'<li>')
                _tmp3 = _path(submenu, econtext['request'], True, 'title')
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
                _write(u'\n              ')
                attrs = _attrs_4464452432
                'submenu/children'
                _write(u'<ul>\n                ')
                _tmp3 = _path(submenu, econtext['request'], True, 'children')
                entry = None
                (_tmp3, _tmp4, ) = repeat.insert('entry', _tmp3)
                for entry in _tmp3:
                    _tmp4 = (_tmp4 - 1)
                    attrs = _attrs_4464452560
                    _write(u'<li>')
                    attrs = _attrs_4464452688
                    'join(value("_path(entry, request, True, \'url\')"),)'
                    _write(u'<a')
                    _tmp5 = _path(entry, econtext['request'], True, 'url')
                    if (_tmp5 is _default):
                        _tmp5 = u'${entry/url}'
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
                    'join(parts(value("_path(entry, request, True, \'description\')"), value(\'None\')),)'
                    try:
                        u'entry/description'
                        _tmp7 = _path(entry, econtext['request'], True, 'description')
                    except Exception, e:
                        u'nothing'
                        _tmp7 = None
                    
                    _tmp5 = _tmp7
                    if (_tmp5 is _default):
                        _tmp5 = u'${entry/description|nothing}'
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
                        _write(((' title="' + _tmp5) + '"'))
                    u'entry/title'
                    _write('>')
                    _tmp5 = _path(entry, econtext['request'], True, 'title')
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
                    _write(u'</a></li>')
                    if (_tmp4 == 0):
                        break
                    _write(' ')
                _write(u'\n              </ul>\n            </li>')
                if (_tmp2 == 0):
                    break
                _write(' ')
            _write(u'\n          </ul>\n        </li>\n        ')
            'Modify portal content'
            _tmp1 = _checkPermission(econtext['context'], 'Modify portal content')
            if _tmp1:
                pass
                attrs = _attrs_4464451728
                _write(u'<li>\n          ')
                attrs = _attrs_4464452368
                'join(value("_path(context, request, True, \'absolute_url\')"), u\'/@@edit\')'
                _write(u'<a')
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
                u"%(translate)s('menu_edit', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write('>')
                _result = _translate('menu_edit', domain=_domain, mapping=None, target_language=target_language, default=_marker)
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
                _write(u'</a>\n        </li>')
            _write(u'\n      ')
        _write(u'\n    </ul>\n\n  ')
        attrs = _attrs_4464451088
        'tools/portal/++resource++NuPlone.libraries/jquery-1.4.2.js'
        _write(u'<script type="text/javascript"')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.libraries', 'jquery-1.4.2.js')
        if (_tmp1 is _default):
            _tmp1 = None
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
            _write(((' src="' + _tmp1) + '"'))
        _write(u'></script>\n  ')
        attrs = _attrs_4464451344
        'tools/portal/++resource++NuPlone.behaviour/behaviour.js'
        _write(u'<script type="text/javascript"')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.behaviour', 'behaviour.js')
        if (_tmp1 is _default):
            _tmp1 = None
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
            _write(((' src="' + _tmp1) + '"'))
        'view/actions'
        _write(u'></script>\n  ')
        menu = _path(econtext['view'], econtext['request'], True, 'actions')
        try:
            'menu/url'
            url = _path(menu, econtext['request'], True, 'url')
        except Exception, e:
            'nothing'
            url = None
        
        u'not(_path(url, request, True, ))'
        _tmp1 = not _path(url, econtext['request'], True)
        if _tmp1:
            pass
            attrs = _attrs_4464452240
            _write(u'<script type="text/javascript">\n        $("a.contextActions").click(function(event) {\n                event.preventDefault();\n        })\n  </script>')
        _write(u'\n  ')
        attrs = _attrs_4464452496
        _write(u'<script type="text/javascript">\nvar sitemenu = {\n    // Timer to control hiding of the sitemenu in the main document\n    timer: null,\n\n    getIframeElement: function() {\n        var contentDoc = window.frameElement.ownerDocument,\n            $iframe = $("#siteMenu", contentDoc);\n        return $iframe;\n    },\n\n    clearTimer: function() {\n        if (sitemenu.timer) {\n            clearTimeout(sitemenu.timer);\n            sitemenu.timer = null;\n        }\n    },\n\n    setTimer: function() {\n        if (sitemenu.timer) {\n            return;\n        }\n\n        sitemenu.timer = setTimeout(function() {\n            sitemenu.getIframeElement().css("height", null);\n            }, 1000);\n    },\n\n    init: function() {\n        $("#siteMenu").live("mouseover", function(e) {\n            if (!sitemenu.clearTimer()) {\n                sitemenu.getIframeElement().css("height", "100%");\n            }\n        });\n\n        $("#siteMenu").live("mouseout", function(e) {\n            sitemenu.clearTimer();\n            sitemenu.setTimer();\n        });\n    }\n};\n\nsitemenu.init();\n  </script>\n  </body>\n</html>')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/skin/templates/sitemenu.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
