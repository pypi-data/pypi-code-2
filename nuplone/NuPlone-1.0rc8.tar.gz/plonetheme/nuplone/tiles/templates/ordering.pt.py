registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _attrs_4499820368 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4499845200 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
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
        _write(u'\n  ')
        attrs = _attrs_4499820368
        _write(u'<script type="text/javascript">\n//  ')
        attrs = _attrs_4499845200
        _write(u'<![CDATA[\n$(document).ready(function() {\n    $(".sortable").sortable({containment: "parent" });\n});\n$(".sortable").live("sortstop", function(e, ui) {\n    var order = $.map($(".sortable > *"), function(e) { return e.id;} );\n    $.post(plone.context_url+"/@@update-order", {order: order});\n});\n// ]]>\n  </script>\n')
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/tiles/templates/ordering.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
