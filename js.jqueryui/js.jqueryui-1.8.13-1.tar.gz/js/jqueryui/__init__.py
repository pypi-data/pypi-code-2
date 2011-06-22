from fanstatic import Library, Resource
import js.jquery

library = Library('jqueryui', 'resources')

jqueryui = Resource(library, 'ui/jquery-ui.js',
    minified='ui/minified/jquery-ui.min.js',
    depends=[js.jquery.jquery])

base = Resource(library, 'themes/base/jquery-ui.css',
                         minified='themes/base/minified/jquery-ui.min.css')
black_tie = Resource(library, 'themes/black-tie/jquery-ui.css')
blitzer = Resource(library, 'themes/blitzer/jquery-ui.css')
cupertino = Resource(library, 'themes/cupertino/jquery-ui.css')
dark_hive = Resource(library, 'themes/dark-hive/jquery-ui.css')
dot_luv = Resource(library, 'themes/dot-luv/jquery-ui.css')
eggplant = Resource(library, 'themes/eggplant/jquery-ui.css')
excite_bike = Resource(library, 'themes/excite-bike/jquery-ui.css')
flick = Resource(library, 'themes/flick/jquery-ui.css')
hot_sneaks = Resource(library, 'themes/hot-sneaks/jquery-ui.css')
humanity = Resource(library, 'themes/humanity/jquery-ui.css')
le_frog = Resource(library, 'themes/le-frog/jquery-ui.css')
mint_choc = Resource(library, 'themes/mint-choc/jquery-ui.css')
overcast = Resource(library, 'themes/overcast/jquery-ui.css')
pepper_grinder = Resource(library, 'themes/pepper-grinder/jquery-ui.css')
redmond = Resource(library, 'themes/redmond/jquery-ui.css')
smoothness = Resource(library, 'themes/smoothness/jquery-ui.css')
south_street = Resource(library, 'themes/south-street/jquery-ui.css')
start = Resource(library, 'themes/start/jquery-ui.css')
sunny = Resource(library, 'themes/sunny/jquery-ui.css')
swanky_purse = Resource(library, 'themes/swanky-purse/jquery-ui.css')
trontastic = Resource(library, 'themes/trontastic/jquery-ui.css')
ui_darkness = Resource(library, 'themes/ui-darkness/jquery-ui.css')
ui_lightness = Resource(library, 'themes/ui-lightness/jquery-ui.css')
vader = Resource(library, 'themes/vader/jquery-ui.css')

jqueryui_i18n = Resource(library, 'ui/i18n/jquery-ui-i18n.js',
    minified='ui/minified/i18n/jquery-ui-i18n.min.js',
    depends=[js.jquery.jquery, jqueryui])

