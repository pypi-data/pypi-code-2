registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
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
        u"''"
        _write(u'\n  ')
        _default.value = default = ''
        'view/tiles'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'tiles')
        tile = None
        (_tmp1, _tmp2, ) = repeat.insert('tile', _tmp1)
        for tile in _tmp1:
            _tmp2 = (_tmp2 - 1)
            'tile'
            _content = _path(tile, econtext['request'], True)
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
        _write(u'\n')
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/tiles/templates/group.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
