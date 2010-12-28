
from quantumcore.resources import css_from_pkg_stream, CSSResourceManager, JSResourceManager
from quantumcore.resources import js_from_pkg_stream, JSCluster, CSSCluster

class TestOrdering:
    
    def test_different_names(self):
        script1 = js_from_pkg_stream(__name__, 'data/script1.js', name="1", merge = True, prio=1)
        script2 = js_from_pkg_stream(__name__, 'data/script2.js', name="1", merge = True, prio=2)
        script3 = js_from_pkg_stream(__name__, 'data/script1.js', name="2", merge = True, prio=1)
        script4 = js_from_pkg_stream(__name__, 'data/script2.js', name="2",merge = True, prio=2)

        resources = JSResourceManager([script1, script2, script3, script4], prefix_url="/static/js")

        links1 = resources("1")
        links2 = resources("2")

        # both should merge together to one file each
        # there was a bug though which sorted by prio only, ignoring the name. then you have 
        # changing names 1-2-1-2 which makes it 4 lines. This is wrong though.
        assert len(links1.split("\n")) == 1
        assert len(links2.split("\n")) == 1

