from fanstatic import Library, Resource, Group
import js.modernizr
import js.jquery

library = Library('html5boilerplate', 'resources')

style = Resource(library, 'css/style.css', minified='css/style-min.css')

handheld = Resource(library, 'css/handheld.css', minified='css/handheld-min.css')

def render_pngfix(url):
  return '''<!--[if lt IE 7 ]>
    <script src="%s"></script>
    <script>DD_belatedPNG.fix("img, .png_bg");
  <![endif]-->''' % url

pngfix = Resource(library, 'js/dd_belatedpng.js', renderer=render_pngfix, bottom=True)

boilerplate = Group([js.jquery.jquery, js.modernizr.modernizr, pngfix, style])
