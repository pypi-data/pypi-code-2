from fanstatic import Library, Resource

library = Library('less', 'resources')

lesscss_js = Resource(library, 'less.min.js', bottom=True)
lesscss = lesscss_js
