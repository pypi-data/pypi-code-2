from fanstatic import Library, Resource

library = Library('js.ace', 'resources')

ace = Resource(
    library,
    'ace-uncompressed.js',
    minified='ace.js'
)

cockpit = Resource(
    library,
    'cockpit-uncompressed.js',
    minified='cockpit.js'
)

keybinding_emacs = Resource(library, 'keybinding-emacs.js')
keybinding_vim   = Resource(library, 'keybinding-vim.js')

mode_c_cpp       = Resource(library, 'mode-c_cpp.js')
mode_coffee      = Resource(library, 'mode-coffee.js')
mode_css         = Resource(library, 'mode-css.js')
mode_html        = Resource(library, 'mode-html.js')
mode_java        = Resource(library, 'mode-java.js')
mode_javascript  = Resource(library, 'mode-javascript.js')
mode_php         = Resource(library, 'mode-php.js')
mode_python      = Resource(library, 'mode-python.js')
mode_ruby        = Resource(library, 'mode-ruby.js')
mode_xml         = Resource(library, 'mode-xml.js')

theme_clouds          = Resource(library, 'theme-clouds.js')
theme_clouds_midnight = Resource(library, 'theme-clouds_midnight.js')
theme_cobalt          = Resource(library, 'theme-cobalt.js')
theme_dawn            = Resource(library, 'theme-dawn.js')
theme_eclipse         = Resource(library, 'theme-eclipse.js')
theme_idle_fingers    = Resource(library, 'theme-idle_fingers.js')
theme_kr_theme        = Resource(library, 'theme-kr_theme.js')
theme_mono_industrial = Resource(library, 'theme-mono_industrial.js')
theme_monokai         = Resource(library, 'theme-monokai.js')
theme_pastel_on_dark  = Resource(library, 'theme-pastel_on_dark.js')
theme_twilight        = Resource(library, 'theme-twilight.js')

worker_javascript = Resource(library, 'worker-javascript.js')
