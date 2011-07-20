from fanstatic import Library, Resource

library = Library('fout-b-gone', 'resources')

foutbgone = Resource(library, 'foutbgone.js')

def render_init(url):
    return '''<script type="text/javascript">fbg.hideFOUT('asap');</script>'''
    
foutbgone_init = Resource(library, 'foutbgone_init.js', renderer=render_init, 
    depends=[foutbgone])    