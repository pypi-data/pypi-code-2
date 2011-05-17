registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _attrs_4514069648 = _loads('(dp1\nVmedia\np2\nVall\np3\nsVhref\np4\nV${tools/portal/++resource++NuPlone.style}/form/base.css\np5\nsVrel\np6\nVstylesheet\np7\nsVtype\np8\nVtext/css\np9\ns.')
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _marker = _loads("ccopy_reg\n_reconstructor\np1\n(cchameleon.core.i18n\nStringMarker\np2\nc__builtin__\nstr\np3\nS''\ntRp4\n.")
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _attrs_4514078672 = _loads('(dp1\n.')
    _attrs_4514078608 = _loads('(dp1\nVxmlns\np2\nVhttp://www.w3.org/1999/xhtml\np3\ns.')
    _attrs_4514075536 = _loads('(dp1\n.')
    _attrs_4514070352 = _loads('(dp1\nVsrc\np2\nV${tools/portal/++resource++NuPlone.libraries}/jquery-1.4.2.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4514067280 = _loads('(dp1\nVtype\np2\nVtext/javascript\np3\ns.')
    _attrs_4514070480 = _loads('(dp1\nVaction\np2\nV${request/getURL}\np3\nsVmethod\np4\nV${view/method}\np5\nsVenctype\np6\nV${view/enctype}\np7\ns.')
    _attrs_4514069456 = _loads('(dp1\nVid\np2\nVlinks\np3\nsVclass\np4\nVdropSheet\np5\ns.')
    _attrs_4514070096 = _loads('(dp1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4514067536 = _loads('(dp1\nVname\np2\nVform.buttons.cancel\np3\nsVtype\np4\nVbutton\np5\nsVclass\np6\nVcancel\np7\ns.')
    _attrs_4514067472 = _loads('(dp1\nVname\np2\nVform.buttons.save\np3\nsVtype\np4\nVbutton\np5\nsVclass\np6\nVsave\np7\ns.')
    _attrs_4514069392 = _loads('(dp1\nVcontent\np2\nVtext/html; charset=utf-8\np3\nsVhttp-equiv\np4\nVContent-Type\np5\ns.')
    _attrs_4514066576 = _loads('(dp1\nVclass\np2\nVconcise\np3\ns.')
    _attrs_4514066768 = _loads('(dp1\nVclass\np2\nVbuttonBar\np3\ns.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _attrs_4514066640 = _loads('(dp1\nVsrc\np2\nV${tools/portal/++resource++NuPlone.libraries}/jquery.form.js\np3\nsVtype\np4\nVtext/javascript\np5\ns.')
    _attrs_4514070224 = _loads('(dp1\nVid\np2\nVexternal\np3\nsVclass\np4\nVformSection\np5\ns.')
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
        attrs = _attrs_4514078608
        _write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n  ')
        attrs = _attrs_4514078672
        _write(u'<head>\n    ')
        attrs = _attrs_4514069392
        _write(u'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n    ')
        attrs = _attrs_4514069648
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
        attrs = _attrs_4514069456
        _write(u'<body id="links" class="dropSheet">\n    ')
        attrs = _attrs_4514070096
        u"%(translate)s('header_place_link', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<h1>')
        _result = _translate('header_place_link', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Place a Link')
        _write(u'</h1>\n\n    ')
        attrs = _attrs_4514070224
        _write(u'<div id="external" class="formSection">\n      ')
        attrs = _attrs_4514070480
        'join(value("_path(request, request, True, \'getURL\')"),)'
        _write(u'<form')
        _tmp1 = _path(econtext['request'], econtext['request'], True, 'getURL')
        if (_tmp1 is _default):
            _tmp1 = u'${request/getURL}'
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
        'join(value("_path(view, request, True, \'method\')"),)'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'method')
        if (_tmp1 is _default):
            _tmp1 = u'${view/method}'
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
            _write(((' method="' + _tmp1) + '"'))
        'join(value("_path(view, request, True, \'enctype\')"),)'
        _tmp1 = _path(econtext['view'], econtext['request'], True, 'enctype')
        if (_tmp1 is _default):
            _tmp1 = u'${view/enctype}'
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
            _write(((' enctype="' + _tmp1) + '"'))
        _write(u'>\n        ')
        attrs = _attrs_4514066576
        u"''"
        _write(u'<fieldset class="concise">\n          ')
        _default.value = default = ''
        'view/widgets/URL/render'
        _content = _path(econtext['view'], econtext['request'], True, 'widgets', 'URL', 'render')
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
        u"''"
        _write(u'\n          ')
        _default.value = default = ''
        'view/widgets/title/render'
        _content = _path(econtext['view'], econtext['request'], True, 'widgets', 'title', 'render')
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
        u"''"
        _write(u'\n          ')
        _default.value = default = ''
        'view/widgets/new_window/render'
        _content = _path(econtext['view'], econtext['request'], True, 'widgets', 'new_window', 'render')
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
        _write(u'\n        </fieldset>\n        ')
        attrs = _attrs_4514066768
        _write(u'<div class="buttonBar">\n          ')
        attrs = _attrs_4514067472
        u"%(translate)s('button_save_changes', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<button name="form.buttons.save" class="save" type="button">')
        _result = _translate('button_save_changes', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Save changes')
        _write(u'</button>\n          ')
        attrs = _attrs_4514067536
        u"%(translate)s('button_cancel', domain=%(domain)s, mapping=None, target_language=%(language)s, default=_marker)"
        _write(u'<button name="form.buttons.cancel" class="cancel" type="button">')
        _result = _translate('button_cancel', domain=_domain, mapping=None, target_language=target_language, default=_marker)
        u'%(result)s is not %(marker)s'
        _tmp1 = (_result is not _marker)
        if _tmp1:
            pass
            u'_result'
            _tmp2 = _result
            _write(_tmp2)
        else:
            pass
            _write(u'Cancel')
        _write(u'</button>\n        </div>\n      </form>\n    </div>\n    ')
        attrs = _attrs_4514070352
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
        attrs = _attrs_4514066640
        'join(value("_path(tools, request, True, \'portal\', \'++resource++NuPlone.libraries\')"), u\'/jquery.form.js\')'
        _write(u'<script type="text/javascript"')
        _tmp1 = ('%s%s' % (_path(tools, econtext['request'], True, 'portal', '++resource++NuPlone.libraries'), '/jquery.form.js', ))
        if (_tmp1 is _default):
            _tmp1 = u'${tools/portal/++resource++NuPlone.libraries}/jquery.form.js'
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
        attrs = _attrs_4514067280
        _write(u'<script type="text/javascript">\n// ')
        attrs = _attrs_4514075536
        _write(u'<![CDATA[\n    function reset() {\n        $("input[type=text]").val(null);\n        $("input[type=checkbox]").attr("checked", "checked");\n        $("em.message.warning").remove();\n    }\n\n    function hide() {\n        var topDoc = window.frameElement.ownerDocument;\n        $("#linkFrame", topDoc).hide();\n    }\n\n\n    function show(el) {\n        var topDoc = window.frameElement.ownerDocument;\n\n        if (el===undefined) {\n            reset();\n        } else {\n            var topWindow = topDoc.defaultView!==undefined ? topDoc.defaultView : topDoc.parentWindow,\n                $link = $(el),\n                link = $link.attr("href") || "",\n                title = $link.attr("title") || "",\n                newwindow = $link.attr("target")==="_blank";\n            \n            topWindow.getSelection().selectAllChildren(el);\n            $("input[name=form.widgets.new_window:list]").get(0).checked = newwindow;\n            $("input[name=form.widgets.URL]").val(link);\n            $("input[name=form.widgets.title]").val(title);\n        }\n\n        $("#linkFrame", topDoc).show();\n    }\n\n\n    function getSelectionAnchor(window, document) {\n        if (window.getSelection) {\n            return window.getSelection().anchorNode;\n        } else {\n            // Internet Explorer\n            return document.selection.createRange().parentElement();\n        }\n    }\n\n    // http://www.quirksmode.org/dom/range_intro.html\n    function getSelectionObject(window, document) {\n        if (window.getSelection) {\n            return window.getSelection();\n        } else {\n            return document.selection.createRange();\n        }\n    } \n\n    // http://www.quirksmode.org/dom/range_intro.html\n    function getRangeObject(selectionObject) {\n        if (selectionObject.getRangeAt) {\n              return selectionObject.getRangeAt(0);\n        } else { // Safari!\n            var range = document.createRange();\n            range.setStart(selectionObject.anchorNode,selectionObject.anchorOffset);\n            range.setEnd(selectionObject.focusNode,selectionObject.focusOffset);\n            return range;\n        }\n    }\n\n    function removeLink() {\n        var topDoc = window.frameElement.ownerDocument,\n            topWindow = topDoc.defaultView!==undefined ? topDoc.defaultView : topDoc.parentWindow,\n            $anchor = $(getSelectionAnchor(topWindow, topDoc)),\n            $link;\n\n        // XXX: handle IE where there is no selection and we need to create a new range based on\n        // the cursor position \n        $link=$anchor.closest("a");\n        if (!$link.length){\n            return;\n        }\n\n        $link.replaceWith($link.contents());\n    }\n\n\n    function InsertURL(url, title, newwindow) {\n        var topDoc = window.frameElement.ownerDocument,\n            topWindow = topDoc.defaultView!==undefined ? topDoc.defaultView : topDoc.parentWindow,\n            selection = getSelectionObject(topWindow, topDoc),\n            range, $link;\n\n        if (window.getSelection) {\n            // Modern browsers, using a W3C range object\n            var link = topDoc.createElement("a"),\n                oldlink;\n\n            range = getRangeObject(selection),\n            $link = $(link).attr("href", url).attr("title", title ? title : null);\n\n            if (newwindow) {\n                $link.attr("target", "_blank");\n            }\n\n            if (range.collapsed) {\n                $link.text(title);\n                range.insertNode(link);\n            } else if (selection.anchorNode.nodeType===Node.ELEMENT_NODE &&\n                      selection.anchorNode.tagName.toLowerCase()==="a") {\n                oldlink = selection.anchorNode;\n\n                link.innerHTML=oldlink.innerHTML;\n                try {\n                    oldlink.parentNode.insertBefore(link, oldlink);\n                    $(oldlink).remove();\n                } catch (ex) {\n                    alert(ex);\n                }\n            } else if (selection.anchorNode.nodeType===Node.TEXT_NODE &&\n                      selection.anchorNode.parentNode.nodeType===Node.ELEMENT_NODE &&\n                      selection.anchorNode.parentNode.tagName.toLowerCase()==="a") {\n                // Safari bug: selection.selectAllChildren should include the top node\n                // as well, but instead only its children are added.\n                oldlink = selection.anchorNode.parentNode;\n\n                link.innerHTML=oldlink.innerHTML;\n                try {\n                    oldlink.parentNode.insertBefore(link, oldlink);\n                    $(oldlink).remove();\n                } catch (e) {\n                    alert(e);\n                }\n            } else {\n                try {\n                    range.surroundContents(link);\n                } catch(err) {\n                    /* Workaround for https://bugzilla.mozilla.org/show_bug.cgi?id=520001 */\n                    link.appendChild(range.extractContents());\n                    range.insertNode(link);\n                    range.selectNode(link);\n                }\n            }\n        } else {\n            // Special code path for IE\n            range=selection;\n            $link = $(range.parentElement()).closest("a");\n\n            if ($link.length) {\n                // The selection is inside a link, so update it\n                $link\n                    .attr("href", url)\n                    .attr("target", newwindow ? "_blank" : null)\n                    .attr("title", title ? title : null);\n            } else {\n                range.execCommand("CreateLink", false, url);\n                $link=$(range.parentElement());\n                if (title) {\n                    $link.attr("title", title);\n                }\n                if (newwindow) {\n                    $link.attr("target", "_blank");\n                }\n                if (range.text==="") {\n                  $link.text(url);\n                }\n            }\n        }\n    }\n\n    $("button.cancel").live("click", hide);\n\n    $("button.save").live("click", function() {\n        var form = this.form,\n            link = form["form.widgets.URL"].value,\n            title = form["form.widgets.title"].value,\n            newwindow = form["form.widgets.new_window:list"].checked;\n        if (link.indexOf(":")===-1 && link[0]!=="/") {\n            link="http://"+link;\n        }\n        InsertURL(link, title, newwindow);\n        hide();\n    });\n// ]]>\n    </script>\n  </body>\n</html>')
        _domain = _tmp_domain0
        return _out.getvalue()
    return render

__filename__ = '/Users/wichert/Work/syslab/euphorie/Develop/buildout/src/NuPlone/plonetheme/nuplone/z3cform/templates/editlink.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
