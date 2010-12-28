from quantumcore.resources import js_from_pkg_stream, JSCluster, JSResource


class TestJSMinify:
    
    def test_minify(self):
        script1 = js_from_pkg_stream(__name__, 'data/script1.js', minimize_method="jsmin")
        assert script1.data==u'function foo(a,b,c){alert("foo");}\n'

    def test_nominify(self):
        script1 = js_from_pkg_stream(__name__, 'data/script1.js', minimize_method=None)
        assert script1.data==u'function foo (param1, param2, param3) { alert("foo"); }'