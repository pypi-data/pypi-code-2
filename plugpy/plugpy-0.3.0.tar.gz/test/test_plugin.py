from plugpy import load_plugins, reload_plugins, dispatch

config = dict()
plugin_path='./test/plugin'
debug=True


def test_load():
    res = load_plugins(config, plugin_path=plugin_path, debug=debug)
    assert res != None
    assert len(res) == 3

def test_dispath():
    res = reload_plugins(config, plugin_path=plugin_path, debug=debug)
    res = dispatch('test', 1,2)
    assert res != None
    assert len(res) == 2
    assert res[0][0] == 3

def test_reload_dispath():
    res = reload_plugins(config, plugin_path=plugin_path, debug=debug)
    res = dispatch('test', 1,2)
    assert res != None
    assert len(res) == 2
    assert res[0][0] == 3

def test_dispath_noargs():
    res = reload_plugins(config, plugin_path=plugin_path, debug=debug)
    res = dispatch('test2')
    assert res != None
    assert len(res) == 1
    assert res[0][0] == "test"

def test_alias_dispatch():
    res = reload_plugins(config, plugin_path=plugin_path, debug=debug)
    res = dispatch('test', 1,2, target="#test")
    assert res != None
    assert len(res) == 1
    assert res[0][0] == 3

def test_target_missing_dispatch():
    res = reload_plugins(config, plugin_path=plugin_path, debug=debug)
    res = dispatch('test', 1,2, target="#test_fail")
    assert res == None

#def test_import_modules():
#    import_modules("../werkzeug-main/werkzeug/")
#    assert True

