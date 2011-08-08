from libacr.lib import IconLink, url

import tw.forms as twf
from tw.api import JSLink

adv_file_field_js = JSLink(modname='libacr', filename='static/advfile.js')

class AdvancedFileField(twf.FormField):
    icons = {'trash':IconLink(modname='libacr',
                        filename='static/icons/trash.png', alt='Trash'),
             'upload':IconLink(modname='libacr',
                        filename='static/icons/upload.png', alt='Upload')
            }
    params = ['icons']
    template = "libacr.templates.form_fields.advanced_file_field"
    javascript = [adv_file_field_js]
    file_upload = True


class AssetField(twf.FormField):
    template = "libacr.templates.form_fields.asset_field"
    javascript = [JSLink(modname='libacr', filename='static/asset.js')]
    icons = {'upload':IconLink(modname='libacr',
                        filename='static/icons/upload.png', alt='Upload'),
             'choose':IconLink(modname='libacr',
                        filename='static/icons/pick.png', alt='Choose')
            }
    assets_box_url = None
    assets_upload_url = None
    params = ['icons', 'assets_box_url', 'assets_upload_url']

    def prepare_dict(self, value, d, adapt=True):
        from libacr.model.core import DBSession
        from libacr.model.assets import Asset

        d = super(AssetField, self).prepare_dict(value, d, adapt)
        if not d['assets_box_url']:
            d['assets_box_url'] = url('/admin/assets/box')

        if not d['assets_upload_url']:
            d['assets_upload_url'] = url('/admin/assets')

        value = d['value']
        asset = None
        if not value:
            value = ''
        elif hasattr(value, 'startswith') and value.startswith('asset'):
            trash, asset_id = value.split(':')
            asset = DBSession.query(Asset).filter_by(uid=asset_id).first()
        
        d['value_id'] = value

        if asset:
            d['value_name'] = asset.name
        else:
            d['value_name'] = value

        return d
