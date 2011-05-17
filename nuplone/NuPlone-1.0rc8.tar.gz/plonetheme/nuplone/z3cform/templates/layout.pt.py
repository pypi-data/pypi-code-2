registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
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
            u"''"
            _write(u'\n     ')
            _default.value = default = ''
            'view/contents'
            _content = _path(econtext['view'], econtext['request'], True, 'contents')
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
            _write(u'\n')
        u"{'content': _callback_content, 'title': _callback_title}"
        _tmp = {'content': _callback_content, 'title': _callback_title, }
        'context/@@layout/macros/layout'
        _metal.render(_tmp, _out=_out, _write=_write, _domain=_domain, econtext=econtext)
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/z3cform/templates/layout.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
