from fanstatic import Resource, GroupResource
from js.extjs import adapter
from js.extjs.library import library

js = Resource(library, 'ext-all.js', depends=[adapter.ext],
              debug='ext-all-debug-w-comments.js')

css = Resource(library, 'resources/css/ext-all.css')

basic = all = GroupResource([adapter.ext, js, css])
