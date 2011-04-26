registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _attrs_4508959696 = _loads('(dp1\nVclass\np2\nVadditionalImages\np3\ns.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4508994896 = _loads('(dp1\n.')
    _attrs_4509028432 = _loads('(dp1\nVhref\np2\nV${solution/url}\np3\ns.')
    _attrs_4508933264 = _loads('(dp1\nVclass\np2\nVintroduction\np3\ns.')
    _attrs_4508959824 = _loads('(dp1\nVsrc\np2\nV${scale/url}\np3\nsVtitle\np4\nV${context/caption4}\np5\nsVwidth\np6\nV${scale/width}\np7\nsValt\np8\nV\nsVclass\np9\nVspan-4\np10\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4508995472 = _loads('(dp1\nVid\np2\nVsolution-${solution/id}\np3\ns.')
    _attrs_4508959632 = _loads('(dp1\nVsrc\np2\nV${scale/url}\np3\nsVtitle\np4\nV${context/caption2}\np5\nsVwidth\np6\nV${scale/width}\np7\nsValt\np8\nV\nsVclass\np9\nVspan-4\np10\ns.')
    _attrs_4508586832 = _loads('(dp1\n.')
    _path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
    _attrs_4508933392 = _loads('(dp1\nVclass\np2\nVsurveyQuestion\np3\ns.')
    _attrs_4508995088 = _loads('(dp1\n.')
    _attrs_4508994768 = _loads('(dp1\n.')
    _attrs_4508193488 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4508266896 = _loads('(dp1\n.')
    _attrs_4508994960 = _loads('(dp1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _attrs_4506155152 = _loads('(dp1\n.')
    _attrs_4508959056 = _loads('(dp1\nVsrc\np2\nV${scale/url}\np3\nsVtitle\np4\nV${context/caption3}\np5\nsVwidth\np6\nV${scale/width}\np7\nsValt\np8\nV\nsVclass\np9\nVspan-4\np10\ns.')
    _attrs_4506097552 = _loads('(dp1\n.')
    _attrs_4508995280 = _loads('(dp1\n.')
    _attrs_4508959504 = _loads('(dp1\n.')
    _attrs_4508267088 = _loads('(dp1\n.')
    _attrs_4508960208 = _loads('(dp1\n.')
    _attrs_4508995024 = _loads('(dp1\n.')
    _attrs_4508959568 = _loads('(dp1\n.')
    _attrs_4508959888 = _loads('(dp1\n.')
    _attrs_4508149008 = _loads('(dp1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4508114640 = _loads('(dp1\n.')
    _attrs_4508994704 = _loads('(dp1\n.')
    _attrs_4508959184 = _loads('(dp1\nVclass\np2\nVclear\np3\ns.')
    _attrs_4508994832 = _loads('(dp1\n.')
    _attrs_4509028496 = _loads('(dp1\n.')
    _attrs_4508150096 = _loads('(dp1\n.')
    _lookup_tile = _loads('cplonetheme.nuplone.tiles.tales\n_lookup_tile\np1\n.')
    _attrs_4506075216 = _loads('(dp1\n.')
    _attrs_4508995344 = _loads("(dp1\nVclass\np2\nV${python:'sortable' if can_edit and len(view.solutions)>1 else None}\np3\ns.")
    _attrs_4508605392 = _loads('(dp1\n.')
    _attrs_4508149200 = _loads('(dp1\n.')
    _attrs_4508932816 = _loads('(dp1\nVsrc\np2\nV${scale/url}\np3\nsVtitle\np4\nV${context/caption}\np5\nsVwidth\np6\nV${scale/width}\np7\nsValt\np8\nV\nsVclass\np9\nVspan-4 floatAfter\np10\ns.')
    _attrs_4506097616 = _loads('(dp1\nVclass\np2\nVmessage notice floatBefore\np3\ns.')
    _attrs_4508959440 = _loads('(dp1\nVclass\np2\nVgrid span-13\np3\ns.')
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
            'context/@@images'
            _write(u'\n      ')
            images = _path(econtext['context'], econtext['request'], True, '@@images')
            attrs = _attrs_4508933264
            "images.scale('image', width=190, direction='down')"
            _write(u'<div class="introduction">\n        ')
            scale = _lookup_attr(images, 'scale')('image', width=190, direction='down')
            'scale'
            _tmp1 = _path(scale, econtext['request'], True)
            if _tmp1:
                pass
                attrs = _attrs_4508932816
                'join(value("_path(scale, request, True, \'url\')"),)'
                _write(u'<img')
                _tmp1 = _path(scale, econtext['request'], True, 'url')
                if (_tmp1 is _default):
                    _tmp1 = u'${scale/url}'
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
                'join(value("_path(scale, request, True, \'width\')"),)'
                _tmp1 = _path(scale, econtext['request'], True, 'width')
                if (_tmp1 is _default):
                    _tmp1 = u'${scale/width}'
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
                    _write(((' width="' + _tmp1) + '"'))
                'join(value("_path(context, request, True, \'caption\')"),)'
                _write(u' alt=""')
                _tmp1 = _path(econtext['context'], econtext['request'], True, 'caption')
                if (_tmp1 is _default):
                    _tmp1 = u'${context/caption}'
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
                _write(u' class="span-4 floatAfter" />')
            _write(u'\n        ')
            u"u'Van belang is dat de spuitlans de juiste lengte heeft om rechtopstaand te werken. Een gebogen spuitlans geeft een hogere polsbelasting en wordt daarom afgeraden.'"
            _default.value = default = u'Van belang is dat de spuitlans de juiste lengte heeft om rechtopstaand te werken. Een gebogen spuitlans geeft een hogere polsbelasting en wordt daarom afgeraden.'
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
            'context.image2 or context.image3 or context.image4'
            _write(u'\n        ')
            _tmp1 = (_lookup_attr(econtext['context'], 'image2') or _lookup_attr(econtext['context'], 'image3') or _lookup_attr(econtext['context'], 'image4'))
            if _tmp1:
                pass
                attrs = _attrs_4508959696
                "images.scale('image2', width=190, direction='down')"
                _write(u'<ul class="additionalImages">\n          ')
                scale = _lookup_attr(images, 'scale')('image2', width=190, direction='down')
                'scale'
                _tmp1 = _path(scale, econtext['request'], True)
                if _tmp1:
                    pass
                    attrs = _attrs_4508959504
                    _write(u'<li>')
                    attrs = _attrs_4508959632
                    'join(value("_path(scale, request, True, \'url\')"),)'
                    _write(u'<img')
                    _tmp1 = _path(scale, econtext['request'], True, 'url')
                    if (_tmp1 is _default):
                        _tmp1 = u'${scale/url}'
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
                    'join(value("_path(scale, request, True, \'width\')"),)'
                    _tmp1 = _path(scale, econtext['request'], True, 'width')
                    if (_tmp1 is _default):
                        _tmp1 = u'${scale/width}'
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
                        _write(((' width="' + _tmp1) + '"'))
                    'join(value("_path(context, request, True, \'caption2\')"),)'
                    _write(u' alt=""')
                    _tmp1 = _path(econtext['context'], econtext['request'], True, 'caption2')
                    if (_tmp1 is _default):
                        _tmp1 = u'${context/caption2}'
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
                    _write(u' class="span-4" /></li>')
                _write(u'\n          ')
                "images.scale('image3', width=190, direction='down')"
                scale = _lookup_attr(images, 'scale')('image3', width=190, direction='down')
                'scale'
                _tmp1 = _path(scale, econtext['request'], True)
                if _tmp1:
                    pass
                    attrs = _attrs_4508959568
                    _write(u'<li>')
                    attrs = _attrs_4508959056
                    'join(value("_path(scale, request, True, \'url\')"),)'
                    _write(u'<img')
                    _tmp1 = _path(scale, econtext['request'], True, 'url')
                    if (_tmp1 is _default):
                        _tmp1 = u'${scale/url}'
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
                    'join(value("_path(scale, request, True, \'width\')"),)'
                    _tmp1 = _path(scale, econtext['request'], True, 'width')
                    if (_tmp1 is _default):
                        _tmp1 = u'${scale/width}'
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
                        _write(((' width="' + _tmp1) + '"'))
                    'join(value("_path(context, request, True, \'caption3\')"),)'
                    _write(u' alt=""')
                    _tmp1 = _path(econtext['context'], econtext['request'], True, 'caption3')
                    if (_tmp1 is _default):
                        _tmp1 = u'${context/caption3}'
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
                    _write(u' class="span-4" /></li>')
                _write(u'\n          ')
                "images.scale('image4', width=190, direction='down')"
                scale = _lookup_attr(images, 'scale')('image4', width=190, direction='down')
                'scale'
                _tmp1 = _path(scale, econtext['request'], True)
                if _tmp1:
                    pass
                    attrs = _attrs_4508960208
                    _write(u'<li>')
                    attrs = _attrs_4508959824
                    'join(value("_path(scale, request, True, \'url\')"),)'
                    _write(u'<img')
                    _tmp1 = _path(scale, econtext['request'], True, 'url')
                    if (_tmp1 is _default):
                        _tmp1 = u'${scale/url}'
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
                    'join(value("_path(scale, request, True, \'width\')"),)'
                    _tmp1 = _path(scale, econtext['request'], True, 'width')
                    if (_tmp1 is _default):
                        _tmp1 = u'${scale/width}'
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
                        _write(((' width="' + _tmp1) + '"'))
                    'join(value("_path(context, request, True, \'caption4\')"),)'
                    _write(u' alt=""')
                    _tmp1 = _path(econtext['context'], econtext['request'], True, 'caption4')
                    if (_tmp1 is _default):
                        _tmp1 = u'${context/caption4}'
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
                    _write(u' class="span-4" /></li>')
                _write(u'\n        ')
                _write(u'</ul>')
            _write(u'\n      </div>\n\n      ')
            attrs = _attrs_4508933392
            u"u'Er kan gebruik worden gemaakt van rechte spuitlansen van verschillende lengte.'"
            _write(u'<blockquote class="surveyQuestion">\n        ')
            _default.value = default = u'Er kan gebruik worden gemaakt van rechte spuitlansen van verschillende lengte.'
            'context/title'
            _content = _path(econtext['context'], econtext['request'], True, 'title')
            attrs = _attrs_4508959888
            u'_content'
            _write(u'<p>')
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
            _write(u'</p>\n      </blockquote>\n\n      ')
            attrs = _attrs_4508959440
            _write(u'<dl class="grid span-13">\n      ')
            attrs = _attrs_4508266896
            u"%(translate)s('label_risk_type', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<dt>')
            _result = _translate('label_risk_type', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Risk type')
            u"u'Risk'"
            _write(u'</dt>\n        ')
            _default.value = default = u'Risk'
            'view/type'
            _content = _path(econtext['view'], econtext['request'], True, 'type')
            attrs = _attrs_4508267088
            u'_content'
            _write(u'<dd>')
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
            _write(u'</dd>\n        ')
            attrs = _attrs_4508193488
            u"%(translate)s('label_problem_description', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
            _write(u'<dt>')
            _result = _translate('label_problem_description', domain=_domain, mapping=None, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                _write(u'Inversed statement')
            u"u'Er bestaat geen mogelijkheid om gebruik te maken van rechte spuitlansen van verschillende lengte.'"
            _write(u'</dt>\n        ')
            _default.value = default = u'Er bestaat geen mogelijkheid om gebruik te maken van rechte spuitlansen van verschillende lengte.'
            'context/problem_description'
            _content = _path(econtext['context'], econtext['request'], True, 'problem_description')
            attrs = _attrs_4508150096
            u'_content'
            _write(u'<dd>')
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
            _write(u'</dd>\n        ')
            attrs = _attrs_4508149008
            u'{}'
            _write(u'<dt>')
            _mapping_4508149008 = {}
            u'True'
            _tmp1 = True
            if _tmp1:
                pass
                _tmp_out2 = _out
                _tmp_write2 = _write
                u'_init_stream()'
                (_out, _write, ) = _init_stream()
                attrs = _attrs_4508586832
                u"%(translate)s('risk_show_na_na', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<em>')
                _result = _translate('risk_show_na_na', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp2 = (_result is not _marker)
                if _tmp2:
                    pass
                    u'_result'
                    _tmp3 = _result
                    _write(_tmp3)
                else:
                    pass
                    _write(u'not applicable')
                u'%(out)s.getvalue()'
                _write(u'</em>')
                _mapping_4508149008['na'] = _out.getvalue()
                _write = _tmp_write2
                _out = _tmp_out2
            u"%(translate)s('risk_show_na', domain=%(domain)s, mapping=_mapping_4508149008, target_language=%(language)s, default=_marker)"
            _result = _translate('risk_show_na', domain=_domain, mapping=_mapping_4508149008, target_language=target_language, default=_marker)
            u'%(result)s is not %(marker)s'
            _tmp1 = (_result is not _marker)
            if _tmp1:
                pass
                u'_result'
                _tmp2 = _result
                _write(_tmp2)
            else:
                pass
                u"_mapping_4508149008['na']"
                _write(u"Show '")
                _tmp1 = _mapping_4508149008['na']
                _write((_tmp1 + u"'"))
            'context/show_notapplicable'
            _write(u'</dt>\n        ')
            _tmp1 = _path(econtext['context'], econtext['request'], True, 'show_notapplicable')
            if _tmp1:
                pass
                attrs = _attrs_4508149200
                u"%(translate)s('yes', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<dd>')
                _result = _translate('yes', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Yes')
                _write(u'</dd>')
            u"not(_path(context, request, True, 'show_notapplicable'))"
            _write(u'\n        ')
            _tmp1 = not _path(econtext['context'], econtext['request'], True, 'show_notapplicable')
            if _tmp1:
                pass
                attrs = _attrs_4506075216
                u"%(translate)s('no', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<dd>')
                _result = _translate('no', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'No')
                _write(u'</dd>')
            "context.type=='risk'"
            _write(u'\n        ')
            _tmp1 = (_lookup_attr(econtext['context'], 'type') == 'risk')
            if _tmp1:
                pass
                _write(u'\n          ')
                attrs = _attrs_4506097552
                u"%(translate)s('label_evaluation_method', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<dt>')
                _result = _translate('label_evaluation_method', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Evaluation method')
                u"u'Calculated'"
                _write(u'</dt>\n          ')
                _default.value = default = u'Calculated'
                'view/evaluation_method'
                _content = _path(econtext['view'], econtext['request'], True, 'evaluation_method')
                attrs = _attrs_4508114640
                u'_content'
                _write(u'<dd>')
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
                "context.evaluation_method=='direct'"
                _write(u'</dd>\n          ')
                _tmp1 = (_lookup_attr(econtext['context'], 'evaluation_method') == 'direct')
                if _tmp1:
                    pass
                    _write(u'\n            ')
                    attrs = _attrs_4508605392
                    u"%(translate)s('label_default_priority', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write(u'<dt>')
                    _result = _translate('label_default_priority', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp1 = (_result is not _marker)
                    if _tmp1:
                        pass
                        u'_result'
                        _tmp2 = _result
                        _write(_tmp2)
                    else:
                        pass
                        _write(u'Default priority')
                    u"u'Low'"
                    _write(u'</dt>\n            ')
                    _default.value = default = u'Low'
                    'view/default_priority'
                    _content = _path(econtext['view'], econtext['request'], True, 'default_priority')
                    attrs = _attrs_4506155152
                    u'_content'
                    _write(u'<dd>')
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
                    _write(u'</dd>\n          ')
                "context.evaluation_method=='calculated'"
                _write(u'\n          ')
                _tmp1 = (_lookup_attr(econtext['context'], 'evaluation_method') == 'calculated')
                if _tmp1:
                    pass
                    _write(u'\n            ')
                    attrs = _attrs_4508994704
                    u"%(translate)s('label_default_probability', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write(u'<dt>')
                    _result = _translate('label_default_probability', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp1 = (_result is not _marker)
                    if _tmp1:
                        pass
                        u'_result'
                        _tmp2 = _result
                        _write(_tmp2)
                    else:
                        pass
                        _write(u'Default probability')
                    u"u'Low'"
                    _write(u'</dt>\n            ')
                    _default.value = default = u'Low'
                    'view/default_probability'
                    _content = _path(econtext['view'], econtext['request'], True, 'default_probability')
                    attrs = _attrs_4508994768
                    u'_content'
                    _write(u'<dd>')
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
                    _write(u'</dd>\n            ')
                    attrs = _attrs_4508994832
                    u"%(translate)s('label_default_frequency', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write(u'<dt>')
                    _result = _translate('label_default_frequency', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp1 = (_result is not _marker)
                    if _tmp1:
                        pass
                        u'_result'
                        _tmp2 = _result
                        _write(_tmp2)
                    else:
                        pass
                        _write(u'Default frequency')
                    u"u'Low'"
                    _write(u'</dt>\n            ')
                    _default.value = default = u'Low'
                    'view/default_frequency'
                    _content = _path(econtext['view'], econtext['request'], True, 'default_frequency')
                    attrs = _attrs_4508994896
                    u'_content'
                    _write(u'<dd>')
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
                    _write(u'</dd>\n            ')
                    attrs = _attrs_4508994960
                    u"%(translate)s('label_default_effect', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                    _write(u'<dt>')
                    _result = _translate('label_default_effect', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp1 = (_result is not _marker)
                    if _tmp1:
                        pass
                        u'_result'
                        _tmp2 = _result
                        _write(_tmp2)
                    else:
                        pass
                        _write(u'Default effect')
                    u"u'Low'"
                    _write(u'</dt>\n            ')
                    _default.value = default = u'Low'
                    'view/default_effect'
                    _content = _path(econtext['view'], econtext['request'], True, 'default_effect')
                    attrs = _attrs_4508995024
                    u'_content'
                    _write(u'<dd>')
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
                    _write(u'</dd>\n          ')
                _write(u'')
            _write(u'\n      </dl>\n      ')
            attrs = _attrs_4508959184
            'context.legal_reference'
            _write(u'<hr class="clear" />\n      ')
            _tmp1 = _lookup_attr(econtext['context'], 'legal_reference')
            if _tmp1:
                pass
                attrs = _attrs_4506097616
                _write(u'<div class="message notice floatBefore">\n        ')
                attrs = _attrs_4508995088
                u"%(translate)s('label_legal_reference', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<h4>')
                _result = _translate('label_legal_reference', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Legal and policy references')
                u"u' Rechte spuitlansen van verschillende lengte aanschaffen en gebruiken. Zie ook www.fytostat.nl.'"
                _write(u'</h4>\n        ')
                _default.value = default = u' Rechte spuitlansen van verschillende lengte aanschaffen en gebruiken. Zie ook www.fytostat.nl.'
                'context/legal_reference'
                _content = _path(econtext['context'], econtext['request'], True, 'legal_reference')
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
                _write(u'\n      </div>')
            'view/solutions'
            _write(u'\n      ')
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'solutions')
            if _tmp1:
                pass
                _write(u'\n        ')
                attrs = _attrs_4508995280
                u"%(translate)s('header_solutions', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
                _write(u'<h2>')
                _result = _translate('header_solutions', domain=_domain, mapping=None, target_language=target_language, default=_marker)
                u'%(result)s is not %(marker)s'
                _tmp1 = (_result is not _marker)
                if _tmp1:
                    pass
                    u'_result'
                    _tmp2 = _result
                    _write(_tmp2)
                else:
                    pass
                    _write(u'Standard solutions')
                _write(u'</h2>\n\n        ')
                attrs = _attrs_4508995344
                'join(value("\'sortable\' if can_edit and len(view.solutions)>1 else None"),)'
                _write(u'<ol')
                _tmp1 = ('sortable' if (can_edit and (len(_lookup_attr(econtext['view'], 'solutions')) > 1)) else None)
                if (_tmp1 is _default):
                    _tmp1 = u"${python:'sortable' if can_edit and len(view.solutions)>1 else None}"
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
                'view/solutions'
                _write(u'>\n          ')
                _tmp1 = _path(econtext['view'], econtext['request'], True, 'solutions')
                solution = None
                (_tmp1, _tmp2, ) = repeat.insert('solution', _tmp1)
                for solution in _tmp1:
                    _tmp2 = (_tmp2 - 1)
                    attrs = _attrs_4508995472
                    'join(u\'solution-\', value("_path(solution, request, True, \'id\')"))'
                    _write(u'<li')
                    _tmp3 = ('%s%s' % ('solution-', _path(solution, econtext['request'], True, 'id'), ))
                    if (_tmp3 is _default):
                        _tmp3 = u'solution-${solution/id}'
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
                        _write(((' id="' + _tmp3) + '"'))
                    _write('>')
                    attrs = _attrs_4509028432
                    'join(value("_path(solution, request, True, \'url\')"),)'
                    _write(u'<a')
                    _tmp3 = _path(solution, econtext['request'], True, 'url')
                    if (_tmp3 is _default):
                        _tmp3 = u'${solution/url}'
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
                        _write(((' href="' + _tmp3) + '"'))
                    u'{}'
                    _write('>')
                    _mapping_4509028432 = {}
                    u'True'
                    _tmp3 = True
                    if _tmp3:
                        pass
                        _tmp_out4 = _out
                        _tmp_write4 = _write
                        u'_init_stream()'
                        (_out, _write, ) = _init_stream()
                        u'repeat/solution/number'
                        _tmp4 = _path(repeat, econtext['request'], True, 'solution', 'number')
                        _tmp = _tmp4
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
                        u'%(out)s.getvalue()'
                        _mapping_4509028432['number'] = _out.getvalue()
                        _write = _tmp_write4
                        _out = _tmp_out4
                    u"%(translate)s('risk_solution_header', domain=%(domain)s, mapping=_mapping_4509028432, target_language=%(language)s, default=_marker)"
                    _result = _translate('risk_solution_header', domain=_domain, mapping=_mapping_4509028432, target_language=target_language, default=_marker)
                    u'%(result)s is not %(marker)s'
                    _tmp3 = (_result is not _marker)
                    if _tmp3:
                        pass
                        u'_result'
                        _tmp4 = _result
                        _write(_tmp4)
                    else:
                        pass
                        u"_mapping_4509028432['number']"
                        _write(u'Solution ')
                        _tmp3 = _mapping_4509028432['number']
                        _write(_tmp3)
                    _write(u'</a>')
                    attrs = _attrs_4509028496
                    u"''"
                    _write(u'<br />\n          ')
                    _default.value = default = ''
                    'solution/description'
                    _content = _path(solution, econtext['request'], True, 'description')
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
                    _write(u'</li>')
                    if (_tmp2 == 0):
                        break
                    _write(' ')
                _write(u'\n        </ol>\n      ')
            _write(u'')
            _write('\n')
        u"{'content': _callback_content, 'buttonbar': _callback_buttonbar, 'title': _callback_title}"
        _tmp = {'content': _callback_content, 'buttonbar': _callback_buttonbar, 'title': _callback_title, }
        'context/@@layout/macros/layout'
        _metal.render(_tmp, _out=_out, _write=_write, _domain=_domain, econtext=econtext)
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/Euphorie/euphorie/content/templates/risk_view.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
