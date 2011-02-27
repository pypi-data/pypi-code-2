from quantumcore.contenttypes import globs

def pytest_funcarg__gr(request):
    """return a glob registry"""
    gr = globs.GlobRegistry()
    gr.read()
    return gr
