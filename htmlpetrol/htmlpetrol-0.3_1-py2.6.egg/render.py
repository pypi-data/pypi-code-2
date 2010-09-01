try:
    from xml.etree import cElementTree as ElementTree
    from xml.etree.cElementTree import XML
except:
    from xml.etree import ElementTree
    from xml.etree.ElementTree import XML

__tag_behaviour__ = [
    {
        "tag": "input",
        "type": ["text", "hidden", "password", "button", "submit"],
        "property": "value",
        "value": "__literal__"
    },
    {
        "tag": "input",
        "type": ["checkbox"],
        "property": "checked",
        "value": "checked"
    },
    {
        "tag": "input",
        "type": ["radio"],
        "property": "checked",
        "value": "checked"
    },
    {
        "tag": "select",
        "children": ["option"],
        "match": "value",
        "property": "selected",
        "value": "selected"
    },
    {
        "tag": "textarea",
        "property": "__text__",
        "value": "__literal__"
    }
]

def render(html, defaults={}, errors={}):
    html_pre = ""
    html_post = ""
    sbody_start = html.find("<body")
    if sbody_start >= 0:
        cbody_start = html.find("</body")
        cbody_end = html.find(">", cbody_start)
        dom = XML(html[sbody_start:cbody_end+1])
        html_pre = html[0:sbody_start]
        html_post = html[cbody_end+1:]
    else:
        dom = XML(html)

    def apply_to(n, t, d):
        if t["value"] == "__literal__":
            value = d
        else:
            value = t["value"]
        if "children" in t:
            for child_tag in t["children"]:
                for child in n.getiterator(child_tag):
                    if child.attrib.get(t["match"]) == d:
                        child.set(t["property"], value)
        elif t["property"] == "__text__":
            n.text = value
        else:
            n.set(t["property"], value)

    for tag in __tag_behaviour__:
        for node in dom.getiterator(tag["tag"]):
            if node.attrib.get("name") not in defaults:
                continue
            if "type" in tag:
                if node.attrib.get("type") in tag["type"]:
                    apply_to(node, tag,
                             defaults[node.attrib.get("name")])
            else:
                apply_to(node, tag,
                         defaults[node.attrib.get("name")])

    html = "%s%s%s" % (html_pre, ElementTree.tostring(dom, "utf-8"), html_post)

    # Deal with error tags
    for node in dom.getiterator("error"):
        string = ""
        error_tag = '<error for="%s">' % node.attrib.get("for")
        serror_start = html.find(error_tag)
        eerror_start = html.find("</error>", serror_start)
        if node.attrib.get("for") in errors:
            string = None
            for child in node.getiterator():
                # Cheat way to skip over the first element
                if string == None:
                    string = ""
                    continue
                string += ElementTree.tostring(child, "utf-8")
            if string.find("%s") >= 0:
                string = string.replace("#%", "%")
                error_msg = (errors[node.attrib.get("for")])
                if hasattr(error_msg[0], "__iter__"):
                    error_msg = tuple(error_msg[0])
                string = string % error_msg
        html = html[0:serror_start]+string+html[eerror_start+len("</script>")+1:]
    return html
