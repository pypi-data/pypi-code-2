from quantumcore.resources import css_from_pkg_stream, CSSResourceManager, JSResourceManager
from quantumcore.resources import js_from_pkg_stream, JSCluster, CSSCluster


class CSSResourceFixture1:
    """a set of two CSS resources inside a ResourceManager"""

    
    uresource1 = css_from_pkg_stream(__name__, 'data/style.css', merge=False, prio=1)
    uresource2 = css_from_pkg_stream(__name__, 'data/addons.css', merge=False, prio=2)
    unmerged_resources = CSSResourceManager([uresource1, uresource2], prefix_url='/static/css')

    
    mresource1 = css_from_pkg_stream(__name__, 'data/style.css', merge=True, prio=1)
    mresource2 = css_from_pkg_stream(__name__, 'data/addons.css', merge=True, prio=2)
    merged_resources = CSSResourceManager([mresource1, mresource2], prefix_url='/static/css')
    
    ieresource = css_from_pkg_stream(__name__, 'data/ie.css', merge=True, prio=3, name="ie")
    ie_resources = CSSResourceManager([mresource1, mresource2, ieresource], prefix_url='/static/css')
    
    # for printing
    presource1 = css_from_pkg_stream(__name__, 'data/print.css', merge=True, media="print", prio=3)
    print_resources = CSSResourceManager([mresource1, mresource2, presource1], prefix_url='/static/css')
    
        
def pytest_funcarg__cssfix1(request):
    return CSSResourceFixture1()
    
    
class JSResourceFixture1:
    """the same for Javascript resources"""
    
    script1 = js_from_pkg_stream(__name__, 'data/script1.js', merge = False, prio=1)
    script2 = js_from_pkg_stream(__name__, 'data/script2.js', merge = False, prio=2)
    unmerged_resources = JSResourceManager([script1, script2], prefix_url="/static/js")

    script3 = js_from_pkg_stream(__name__, 'data/script1.js', merge = True, prio=1)
    script4 = js_from_pkg_stream(__name__, 'data/script2.js', merge = True, prio=2)
    merged_resources = JSResourceManager([script3, script4], prefix_url="/static/js")

    script5 = js_from_pkg_stream(__name__, 'data/script1.js', merge = True, prio=1)
    script6 = js_from_pkg_stream(__name__, 'data/script2.js', merge = True, prio=2)
    script7 = js_from_pkg_stream(__name__, 'data/script3.js', merge = True, prio=3, name="ie")
    named_resources = JSResourceManager([script5, script6, script7], prefix_url="/static/js")


def pytest_funcarg__jsfix1(request):
    return JSResourceFixture1()
