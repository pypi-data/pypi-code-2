registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4469614160 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
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
        _write(u'\n')
        attrs = _attrs_4469614160
        u'view/account'
        _write(u'<script type="text/javascript">\n  var _gaq = _gaq || [];\n  _gaq.push([\'_setAccount\', \'')
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'account')
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
        'view/domain'
        _write(u"']);\n")
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'domain')
        if _tmp1:
            pass
            u'view/domain'
            _write(u"_gaq.push(['_setDomainName', '")
            _tmp1 = _path(econtext['view'], econtext['request'], True, 'domain')
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
            _write(u"']);")
        u'view/login'
        _write(u"\n  _gaq.push(['_setCustomVar', 1, 'account', '")
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'login')
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
        _write(u"', 3]);\n  _gaq.push(['_trackPageview']);\n\n  (function() {\n    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;\n    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';\n    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);\n  })();\n\n</script>\n")
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/tiles/templates/analytics.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
