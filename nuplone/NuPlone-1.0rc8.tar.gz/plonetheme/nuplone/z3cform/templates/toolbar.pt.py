registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _attrs_4463011792 = _loads('(dp1\nVclass\np2\nVbuttonGroup\np3\ns.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4463011856 = _loads('(dp1\nVtitle\np2\nVUnlink\np3\nsVtype\np4\nVbutton\np5\nsVclass\np6\nVicon unlink\np7\ns.')
    _attrs_4424807248 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVhref\np4\nV${tools/portal/++resource++NuPlone.style}/form/base.css\np5\nsVrel\np6\nVstylesheet\np7\nsVtype\np8\nVtext/css\np9\ns.')
    _attrs_4424761808 = _loads('(dp1\nVsrc\np2\nV${tools/portal/++resource++NuPlone.libraries}/jquery-1.4.2.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4463011408 = _loads('(dp1\nVid\np2\nVeditorFunctions\np3\ns.')
    _attrs_4463012752 = _loads('(dp1\nVtype\np2\nVbutton\np3\nsVclass\np4\nVicon orderedList\np5\ns.')
    _attrs_4452442640 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
    _attrs_4463011472 = _loads('(dp1\nVclass\np2\nVbuttonGroup\np3\ns.')
    _attrs_4463010576 = _loads('(dp1\nVtype\np2\nVbutton\np3\nsVclass\np4\nVicon superscript\np5\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4463010320 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    _attrs_4463011920 = _loads('(dp1\nVtype\np2\nVbutton\np3\nsVclass\np4\nVinline emphasised\np5\ns.')
    _attrs_4463012688 = _loads('(dp1\nVtype\np2\nVbutton\np3\nsVclass\np4\nVinline strong\np5\ns.')
    _attrs_4424762832 = _loads('(dp1\nVid\np2\nVbuttonBar\np3\ns.')
    _attrs_4463012432 = _loads('(dp1\nVtype\np2\nVbutton\np3\nsVclass\np4\nVicon unorderedList\np5\ns.')
    _attrs_4463010064 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _attrs_4463011600 = _loads('(dp1\n.')
    _attrs_4463011536 = _loads('(dp1\nVtype\np2\nVbutton\np3\nsVclass\np4\nVicon subscript\np5\ns.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4452442832 = _loads('(dp1\nVcontent\np2\nVtext/html; charset=utf-8\np3\nsVhttp-equiv\np4\nVContent-Type\np5\ns.')
    _attrs_4463012176 = _loads('(dp1\nVtitle\np2\nVHyperlink\np3\nsVtype\np4\nVbutton\np5\nsVclass\np6\nVicon link\np7\ns.')
    _attrs_4452443856 = _loads('(dp1\n.')
    _attrs_4463010192 = _loads('(dp1\nVclass\np2\nVbuttonGroup\np3\ns.')
    _attrs_4424764304 = _loads('(dp1\nVid\np2\nVeditBar\np3\ns.')
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
        attrs = _attrs_4452442640
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n  ')
        attrs = _attrs_4452443856
        _write(u'<head>\n    ')
        attrs = _attrs_4452442832
        _write(u'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n    ')
        attrs = _attrs_4424807248
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.style\')"), u\'/form/base.css\')'
        _write(u'<link rel="stylesheet" type="text/css" media="all"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.style'), '/form/base.css', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.style}/form/base.css'
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
        _write(u' />\n  </head>\n  ')
        attrs = _attrs_4424764304
        _write(u'<body id="editBar">\n    ')
        attrs = _attrs_4424762832
        _write(u'<div id="buttonBar">\n      ')
        attrs = _attrs_4463011408
        _write(u'<div id="editorFunctions">\n        ')
        attrs = _attrs_4463011600
        _write(u'<fieldset>\n          ')
        attrs = _attrs_4463012688
        _write(u'<button type="button" class="inline strong">B</button>\n          ')
        attrs = _attrs_4463011920
        _write(u'<button type="button" class="inline emphasised">I</button>\n        </fieldset>\n\n        ')
        attrs = _attrs_4463011792
        _write(u'<fieldset class="buttonGroup">\n          ')
        attrs = _attrs_4463012432
        _write(u'<button type="button" class="icon unorderedList">Unordered List</button>\n          ')
        attrs = _attrs_4463012752
        _write(u'<button type="button" class="icon orderedList">Ordered List</button>\n        </fieldset>\n\n        ')
        attrs = _attrs_4463011472
        _write(u'<fieldset class="buttonGroup">\n          ')
        attrs = _attrs_4463011536
        _write(u'<button type="button" class="icon subscript">Subscript</button>\n          ')
        attrs = _attrs_4463010576
        _write(u'<button type="button" class="icon superscript">Superscript</button>\n        </fieldset>\n\n        ')
        attrs = _attrs_4463010192
        _write(u'<fieldset class="buttonGroup">\n          ')
        attrs = _attrs_4463012176
        _write(u'<button type="button" class="icon link" title="Hyperlink">Hyperlink</button>\n          ')
        attrs = _attrs_4463011856
        _write(u'<button type="button" class="icon unlink" title="Unlink">Unlink</button>\n        </fieldset>\n      </div>\n    </div>\n    ')
        attrs = _attrs_4424761808
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.libraries\')"), u\'/jquery-1.4.2.js\')'
        _write(u'<script type="text/javascript"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.libraries'), '/jquery-1.4.2.js', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.libraries}/jquery-1.4.2.js'
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
        attrs = _attrs_4463010064
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
        attrs = _attrs_4463010320
        _write(u'<script type="text/javascript">\n      function getTiny() {\n          var topDoc = window.frameElement.ownerDocument,\n              topWindow = topDoc.defaultView!==undefined ? topDoc.defaultView : topDoc.parentWindow;\n          return topWindow.tinyMCE;\n      }\n\n      function activate(ed) {\n          $("button").show();\n      }\n\n      function deactivate(ed) {\n          $("button").hide();\n      }\n\n      $("#editorFunctions .strong").live("click", function() {\n          getTiny().execCommand("Bold"); return false; });\n      $("#editorFunctions .emphasised").live("click", function() {\n          getTiny().execCommand("italic"); return false; });\n\n      $("#editorFunctions .unorderedList").live("click", function() {\n          getTiny().execCommand("InsertUnorderedList"); return false; });\n      $("#editorFunctions .orderedList").live("click", function() {\n          getTiny().execCommand("InsertOrderedList"); return false; });\n\n      $("#editorFunctions .subscript").live("click", function() {\n          getTiny().execCommand("Subscript"); return false; });\n      $("#editorFunctions .superscript").live("click", function() {\n          getTiny().execCommand("Superscript"); return false; });\n\n      $("#editorFunctions .link").live("click", function() {\n          var topDoc = window.frameElement.ownerDocument,\n              $linkFrame = $("#linkFrame", topDoc);\n\n          $linkFrame.get(0).contentWindow.show();\n      });\n      $("#editorFunctions .unlink").live("click", function() {\n          var topDoc = window.frameElement.ownerDocument,\n              $linkFrame = $("#linkFrame", topDoc);\n\n          $linkFrame.get(0).contentWindow.removeLink();\n      });\n    </script>\n  </body>\n</html>')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/z3cform/templates/toolbar.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
