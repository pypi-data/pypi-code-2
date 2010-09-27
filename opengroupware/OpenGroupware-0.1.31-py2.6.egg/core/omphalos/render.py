# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import time
from render_appointment import render_appointment, render_resource
from render_project     import render_project
from render_contact     import render_contact
from render_enterprise  import render_enterprise
from render_team        import render_team
from render_task        import render_task
from render_blob        import render_folder, render_file
from coils.core         import BundleManager, CoilsException

class Render:
    @staticmethod
    def Results(data, detail, ctx):
        result = [ ]
        for entity in data:
            if (entity is not None):
                if (isinstance(entity, list)):
                    entity = entity[0]
                #ctx.log.debug('rendering result {0}#{1}'.format(entity.__entityName__, entity.object_id))
                result.append(Render.Result(entity, detail, ctx))
        return result

    @staticmethod
    def Result(entity, detail, ctx):
        x = None
        start = time.time()
        method = '_render_{0}'.format(entity.__entityName__.lower())
        if (hasattr(Render, method)):
            # HACK: Preload favorites
            fav_ids = ctx.get_favorited_ids_for_kind(entity.__entityName__, refresh=False)
            # Call render method
            x = getattr(Render, '_render_%s' % entity.__entityName__.lower())(entity, detail, ctx, favorite_ids=fav_ids)
            if (detail & 8192):
                plugin_data = [ ]
                for plugin in BundleManager.get_content_plugins(entity.__entityName__, ctx):
                    if (hasattr(plugin, 'get_extra_content')):
                        data = plugin.get_extra_content(entity)
                        if (data is not None):
                            data.update( { 'entityName': 'PluginData',
                                           'pluginName': plugin.__pluginName__ } )
                            plugin_data.append(data)
                x['_PLUGINDATA'] = plugin_data
            #ctx.log.info('Rendering entity consumed {0}s'.format(time.time() - start))
        else:
            ctx.log.info('Omphalos cannot render entity {0}'.format(entity.__entityName__))
            raise CoilsException('Omphalos cannot render entity {0}'.format(entity.__entityName__))
        return x

    @staticmethod
    def _render_appointment(entity, detail, ctx, favorite_ids=None):
        return render_appointment(entity, detail, ctx)

    @staticmethod
    def _render_contact(entity, detail, ctx, favorite_ids=None):
        return render_contact(entity, detail, ctx, favorite_ids=None)

    @staticmethod
    def _render_enterprise(entity, detail, ctx, favorite_ids=None):
        return render_enterprise(entity, detail, ctx)

    @staticmethod
    def _render_file(entity, detail, ctx, favorite_ids=None):
        return render_file(entity, detail, ctx)

    @staticmethod
    def _render_folder(entity, detail, ctx, favorite_ids=None):
        return render_folder(entity, detail, ctx)

    @staticmethod
    def _render_project(entity, detail, ctx, favorite_ids=None):
        return  render_project(entity, detail, ctx)

    @staticmethod
    def _render_resource(entity, detail, ctx, favorite_ids=None):
        return  render_resource(entity, detail, ctx)

    @staticmethod
    def _render_task(entity, detail, ctx, favorite_ids=None):
        return render_task(entity, detail, ctx)

    @staticmethod
    def _render_team(entity, detail, ctx, favorite_ids=None):
        return render_team(entity, detail, ctx)
