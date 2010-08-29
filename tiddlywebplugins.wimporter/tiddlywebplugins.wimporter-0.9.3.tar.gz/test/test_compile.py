


def test_compile():
    try:
        import tiddlywebplugins.wimporter
        assert True
    except ImportError, exc:
        assert False, exc
