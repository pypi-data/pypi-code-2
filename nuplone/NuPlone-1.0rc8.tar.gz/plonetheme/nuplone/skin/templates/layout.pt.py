registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_4499662608 = _loads('(dp1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4499661840 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVhref\np4\nV${tools/portal/++resource++NuPlone.style/main}/base.css\np5\nsVrel\np6\nVstylesheet\np7\nsVtype\np8\nVtext/css\np9\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _attrs_4499662224 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVhref\np4\nV${tools/portal/++resource++NuPlone.style}/euphorie/base.css\np5\nsVrel\np6\nVstylesheet\np7\nsVtype\np8\nVtext/css\np9\ns.')
    _attrs_4499661648 = _loads('(dp1\nVcontent\np2\nVtext/html; charset=utf-8\np3\nsVhttp-equiv\np4\nVContent-Type\np5\ns.')
    _attrs_4499664400 = _loads('(dp1\nVsrc\np2\nV${tools/portal/++resource++NuPlone.libraries}/ui-1.8/minified/jquery-ui.min.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4499661392 = _loads('(dp1\n.')
    _attrs_4499660880 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
    _attrs_4499663888 = _loads('(dp1\nVsrc\np2\nV${tools/portal/++resource++NuPlone.libraries}/jquery.tools.min.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_4499664592 = _loads('(dp1\nVsrc\np2\nV${tools/portal/++resource++NuPlone.behaviour}/behaviour.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4499664144 = _loads('(dp1\nVtype\np2\nVtext/html\np3\nsVdata\np4\nV${string:${context/absolute_url}/@@sitemenu}?view_type=${tools/view_type}\np5\nsVid\np6\nVsiteMenu\np7\ns.')
    _attrs_4499662864 = _loads('(dp1\nVid\np2\nVcontent\np3\ns.')
    _lookup_tile = _loads('cplonetheme.nuplone.tiles.tales\n_lookup_tile\np1\n.')
    _attrs_4499664720 = _loads('(dp1\nVsrc\np2\nV${tools/portal/++resource++NuPlone.z3cform.js}\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_4499664016 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _attrs_4499664208 = _loads('(dp1\nVid\np2\nVframeWrapper\np3\ns.')
    _attrs_4499664336 = _loads('(dp1\nVsrc\np2\nV${tools/portal/++resource++NuPlone.libraries}/jquery-1.4.4.min.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_4499664464 = _loads('(dp1\nVsrc\np2\nV${tools/portal/++resource++NuPlone.tinymce}/tiny_mce_src.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_4499661456 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    _attrs_4499663312 = _loads('(dp1\n.')
    _attrs_4499661584 = _loads('(dp1\nVsrc\np2\nV${tools/portal/++resource++NuPlone.libraries/css_browser_selector.js}\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_4499662928 = _loads('(dp1\nVid\np2\nVmainContent\np3\ns.')
    _attrs_4499662288 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVtype\np4\nVtext/css\np5\ns.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u"%(scope)s['%(out)s'], %(scope)s['%(write)s']"
        (_out, _write, ) = (econtext['_out'], econtext['_write'], )
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        _tmp_domain0 = _domain
        u"'nuplone'"
        _domain = 'nuplone'
        'context/@@tools'
        tools = _path(econtext['context'], econtext['request'], True, '@@tools')
        attrs = _attrs_4499660880
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n  ')
        attrs = _attrs_4499661456
        _write(u'<head>\n    ')
        attrs = _attrs_4499661648
        _write(u'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n    ')
        attrs = _attrs_4499661584
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.libraries\', \'css_browser_selector.js\')"),)'
        _write(u'<script type="text/javascript"')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.libraries', 'css_browser_selector.js')
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.libraries/css_browser_selector.js}'
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
        attrs = _attrs_4499661840
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.style\', \'main\')"), u\'/base.css\')'
        _write(u'<link rel="stylesheet" type="text/css" media="all"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.style', 'main'), '/base.css', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.style/main}/base.css'
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
        u'tools/portal/++resource++NuPlone.style'
        _write(u' />\n    <!--[if IE 6]> <link rel="stylesheet" type="text/css" media="all" href="')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.style')
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
        u'tools/portal/++resource++NuPlone.style'
        _write(u'/main/base-ie6.css" /> <![endif]-->\n    <!--[if IE 7]> <link rel="stylesheet" type="text/css" media="all" href="')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.style')
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
        u'tools/portal/++resource++NuPlone.style'
        _write(u'/main/base-ie7.css" /> <![endif]-->\n    <!--[if IE 8]> <link rel="stylesheet" type="text/css" media="all" href="')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.style')
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
        _write(u'/main/base-ie8.css" /> <![endif]-->\n    ')
        attrs = _attrs_4499662288
        u"u'Change order of items by dragging the handle'"
        _write(u'<style type="text/css" media="all">\n      ol.sortable:after {\n          content: "')
        _msgid = u'Change order of items by dragging the handle'
        u"%(translate)s(' '.join(%(msgid)s.split()), domain=%(domain)s, mapping=None, target_language=%(language)s, default=%(msgid)s)"
        _result = _translate(_lookup_attr(' ', 'join')(_msgid.split()), domain=_domain, mapping=None, target_language=target_language, default=_msgid)
        u'_result'
        _tmp1 = _result
        _write((_tmp1 + u'";\n       }\n    </style>\n    '))
        attrs = _attrs_4499662224
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.style\')"), u\'/euphorie/base.css\')'
        _write(u'<link rel="stylesheet" type="text/css" media="all"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.style'), '/euphorie/base.css', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.style}/euphorie/base.css'
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
        u'tools/portal/++resource++NuPlone.style'
        _write(u' />\n    <!--[if IE 6]> <link rel="stylesheet" type="text/css" media="all" href="')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.style')
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
        u'tools/portal/++resource++NuPlone.style'
        _write(u'/euphorie/base-ie6.css" /> <![endif]-->\n    <!--[if IE 7]> <link rel="stylesheet" type="text/css" media="all" href="')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.style')
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
        u'tools/portal/++resource++NuPlone.style'
        _write(u'/euphorie/base-ie7.css" /> <![endif]-->\n    <!--[if IE 8]> <link rel="stylesheet" type="text/css" media="all" href="')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.style')
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
        _write(u'/euphorie/base-ie8.css" /> <![endif]-->\n    ')
        attrs = _attrs_4499662608
        u"%(slots)s.get('title')"
        _write(u'<title>')
        _tmp = _slots.get('title')
        u'%(tmp)s is not None'
        _tmp1 = (_tmp is not None)
        if _tmp1:
            pass
            u'isinstance(%(tmp)s, basestring)'
            _tmp2 = isinstance(_tmp, basestring)
            if not _tmp2:
                pass
                econtext.update(dict(rcontext=rcontext, _domain=_domain, tools=tools))
                _tmp(econtext, repeat)
            else:
                pass
                u'%(tmp)s'
                _tmp2 = _tmp
                _tmp = _tmp2
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
        else:
            pass
            _write(u'Page Title')
        u'tools/site_title'
        _write(u' \u2014 ')
        _tmp1 = _path(tools, econtext['request'], True, 'site_title')
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
        _write(u'</title>\n  </head>\n  ')
        attrs = _attrs_4499661392
        _write(u'<body>\n    ')
        attrs = _attrs_4499662864
        _write(u'<div id="content">\n      ')
        attrs = _attrs_4499662928
        u"%(slots)s.get('pagetitle')"
        _write(u'<div id="mainContent">\n        ')
        _tmp = _slots.get('pagetitle')
        u'%(tmp)s is not None'
        _tmp1 = (_tmp is not None)
        if _tmp1:
            pass
            u'isinstance(%(tmp)s, basestring)'
            _tmp2 = isinstance(_tmp, basestring)
            if not _tmp2:
                pass
                econtext.update(dict(rcontext=rcontext, _domain=_domain, tools=tools))
                _tmp(econtext, repeat)
            else:
                pass
                u'%(tmp)s'
                _tmp2 = _tmp
                _tmp = _tmp2
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
        else:
            pass
            _write('')
            attrs = _attrs_4499663312
            u"%(slots)s.get('title')"
            _write(u'<h1>')
            _tmp = _slots.get('title')
            u'%(tmp)s is not None'
            _tmp1 = (_tmp is not None)
            if _tmp1:
                pass
                u'isinstance(%(tmp)s, basestring)'
                _tmp2 = isinstance(_tmp, basestring)
                if not _tmp2:
                    pass
                    econtext.update(dict(rcontext=rcontext, _domain=_domain, tools=tools))
                    _tmp(econtext, repeat)
                else:
                    pass
                    u'%(tmp)s'
                    _tmp2 = _tmp
                    _tmp = _tmp2
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
            else:
                pass
            _write(u'</h1>')
        u"%(slots)s.get('buttonbar')"
        _write(u'\n        ')
        _tmp = _slots.get('buttonbar')
        u'%(tmp)s is not None'
        _tmp1 = (_tmp is not None)
        if _tmp1:
            pass
            u'isinstance(%(tmp)s, basestring)'
            _tmp2 = isinstance(_tmp, basestring)
            if not _tmp2:
                pass
                econtext.update(dict(rcontext=rcontext, _domain=_domain, tools=tools))
                _tmp(econtext, repeat)
            else:
                pass
                u'%(tmp)s'
                _tmp2 = _tmp
                _tmp = _tmp2
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
        else:
            pass
        u"''"
        _write(u'\n        ')
        _default.value = default = ''
        'statusmessages'
        _content = _lookup_tile(econtext['context'], econtext['request'], 'statusmessages')
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
        u"%(slots)s.get('content')"
        _write(u'\n        ')
        _tmp = _slots.get('content')
        u'%(tmp)s is not None'
        _tmp1 = (_tmp is not None)
        if _tmp1:
            pass
            u'isinstance(%(tmp)s, basestring)'
            _tmp2 = isinstance(_tmp, basestring)
            if not _tmp2:
                pass
                econtext.update(dict(rcontext=rcontext, _domain=_domain, tools=tools))
                _tmp(econtext, repeat)
            else:
                pass
                u'%(tmp)s'
                _tmp2 = _tmp
                _tmp = _tmp2
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
        else:
            pass
        u"''"
        _write(u'\n      </div>\n      ')
        _default.value = default = ''
        'navigation'
        _content = _lookup_tile(econtext['context'], econtext['request'], 'navigation')
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
        u"''"
        _write(u'\n    </div>\n    ')
        _default.value = default = ''
        'tabs'
        _content = _lookup_tile(econtext['context'], econtext['request'], 'tabs')
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
        _write(u'\n    ')
        attrs = _attrs_4499664208
        _write(u'<p id="frameWrapper">\n      ')
        attrs = _attrs_4499664144
        u'${context/absolute_url}/@@sitemenu'
        _write(u'<object id="siteMenu" type="text/html"')
        _tmp3 = ('%s%s' % (_path(econtext['context'], econtext['request'], True, 'absolute_url'), '/@@sitemenu', ))
        _tmp1 = ('%s%s%s' % (_tmp3, '?view_type=', _path(tools, econtext['request'], True, 'view_type'), ))
        if (_tmp1 is _default):
            _tmp1 = u'${string:${context/absolute_url}/@@sitemenu}?view_type=${tools/view_type}'
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
            _write(((' data="' + _tmp1) + '"'))
        u"u'Can not open site menu.'"
        _write(u'>\n        ')
        _msgid = u'Can not open site menu.'
        u"%(translate)s(' '.join(%(msgid)s.split()), domain=%(domain)s, mapping=None, target_language=%(language)s, default=%(msgid)s)"
        _result = _translate(_lookup_attr(' ', 'join')(_msgid.split()), domain=_domain, mapping=None, target_language=target_language, default=_msgid)
        u'_result'
        _tmp1 = _result
        u"''"
        _write((_tmp1 + u'\n      </object>\n    </p>\n    '))
        _default.value = default = ''
        'actions'
        _content = _lookup_tile(econtext['context'], econtext['request'], 'actions')
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
        u"''"
        _write(u'\n    ')
        _default.value = default = ''
        'footer'
        _content = _lookup_tile(econtext['context'], econtext['request'], 'footer')
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
        _write(u'\n    ')
        attrs = _attrs_4499664016
        u'tools/portal/absolute_url'
        _write(u'<script type="text/javascript">\n      var plone = { portal_url : \'')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', 'absolute_url')
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
        u'context/absolute_url'
        _write(u"',\n                    context_url : '")
        _tmp1 = _path(econtext['context'], econtext['request'], True, 'absolute_url')
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
        _write(u"' };\n    </script>\n    ")
        attrs = _attrs_4499664336
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.libraries\')"), u\'/jquery-1.4.4.min.js\')'
        _write(u'<script type="text/javascript"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.libraries'), '/jquery-1.4.4.min.js', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.libraries}/jquery-1.4.4.min.js'
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
        attrs = _attrs_4499663888
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.libraries\')"), u\'/jquery.tools.min.js\')'
        _write(u'<script type="text/javascript"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.libraries'), '/jquery.tools.min.js', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.libraries}/jquery.tools.min.js'
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
        attrs = _attrs_4499664400
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.libraries\')"), u\'/ui-1.8/minified/jquery-ui.min.js\')'
        _write(u'<script type="text/javascript"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.libraries'), '/ui-1.8/minified/jquery-ui.min.js', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.libraries}/ui-1.8/minified/jquery-ui.min.js'
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
        attrs = _attrs_4499664464
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.tinymce\')"), u\'/tiny_mce_src.js\')'
        _write(u'<script type="text/javascript"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.tinymce'), '/tiny_mce_src.js', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.tinymce}/tiny_mce_src.js'
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
        attrs = _attrs_4499664720
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.z3cform.js\')"),)'
        _write(u'<script type="text/javascript"')
        _tmp1 = _path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.z3cform.js')
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.z3cform.js}'
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
        attrs = _attrs_4499664592
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.behaviour\')"), u\'/behaviour.js\')'
        _write(u'<script type="text/javascript"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.behaviour'), '/behaviour.js', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.behaviour}/behaviour.js'
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
        u"''"
        _write(u'></script>\n    ')
        _default.value = default = ''
        'scripts'
        _content = _lookup_tile(econtext['context'], econtext['request'], 'scripts')
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
        u"%(slots)s.get('scripts')"
        _write(u'\n    ')
        _tmp = _slots.get('scripts')
        u'%(tmp)s is not None'
        _tmp1 = (_tmp is not None)
        if _tmp1:
            pass
            u'isinstance(%(tmp)s, basestring)'
            _tmp2 = isinstance(_tmp, basestring)
            if not _tmp2:
                pass
                econtext.update(dict(rcontext=rcontext, _domain=_domain, tools=tools))
                _tmp(econtext, repeat)
            else:
                pass
                u'%(tmp)s'
                _tmp2 = _tmp
                _tmp = _tmp2
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
        else:
            pass
        _write(u'\n  </body>\n</html>')
        _domain = _tmp_domain0
        return
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/skin/templates/layout.pt'
registry[('layout', False, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
