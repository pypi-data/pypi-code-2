import formalchemy
from formalchemy import helpers as h
from sqlalchemy.util import OrderedDict
from pylons.i18n import _, ungettext, N_, gettext

from ckan.lib.helpers import literal
import ckan.forms.common as common
import ckan.model as model
import ckan.forms.package as package
from ckan.lib import schema_gov
from ckan.lib import field_types
from formalchemy import helpers as fa_h

__all__ = ['get_gov_fieldset']

class GeoLinkExtraField(common.ConfiguredField):
    def get_configured(self):
        return self.GeoLinkField(self.name).with_renderer(self.GeoLinkRenderer)

    class GeoLinkField(formalchemy.Field):
        def sync(self):
            # save behaviour
            pkg = self.model
	    print self 
            pkg.extras[self.name] = self._deserialise() or []


    class GeoLinkRenderer(formalchemy.fields.FieldRenderer):
         
        def render(self,**kwargs):
            # display behaviour
            #html = "<p>Feature name: <input name=\"geo_link\"></input><button id='search_button' onclick=\"search(this.form.feature_name.value);\">Search</button>"
            
            # html = "<div id=\"placeForm\" class=\"autosuggest-box\"> <p class=\"autosuggest-title\"> <input style=\"margin-left:10px;margin-top:10px;width:360px;font-style:italic;color:#666\" id=\"geographic_link\" name=\"geographic_link\" value=\"Edinburgh...\" onfocus=\"clearSearch(this);\" onkeypress=\"checkEnter(event, 'placeForm')\" /></div>"
            pkg_id = self.field.parent.model.id or ''
            kwargs['value'] = self._tags_string()
            kwargs['size'] = 60
            #kwargs['data-tagcomplete-url'] = h.url_for(controller='tag',
            #        action='autocomplete', id=None)
            #        kwargs['data-tagcomplete-queryparam'] = 'incomplete'
            kwargs['class'] = 'autosuggest-box'

            html = literal(fa_h.text_field(self.name, **kwargs))
             
            return html
        def _tags_string(self):
            tags = self.field.parent.tags.value or self.field.parent.model.tags or []
            if tags:
                tagnames = [ tag.name for tag in tags ]
            else:
                tagnames = []
            return ' '.join(tagnames)

        def _tag_links(self):
            tags = self.field.parent.tags.value or self.field.parent.model.tags or []
            if tags:
                tagnames = [ tag.name for tag in tags ]
            else:
                tagnames = []
            return literal(' '.join([literal('<a href="/tag/read/%s">%s</a>' %
                (str(tag), str(tag))) for tag in tagnames]))


class GeoCoverageExtraField(common.ConfiguredField):
    def get_configured(self):
        return self.GeoCoverageField(self.name).with_renderer(self.GeoCoverageRenderer)

    class GeoCoverageField(formalchemy.Field):
        def sync(self):
            if not self.is_readonly():
                pkg = self.model
                form_regions = self._deserialize() or []
                regions_db = schema_gov.GeoCoverageType.get_instance().form_to_db(form_regions)
                pkg.extras[self.name] = regions_db

    class GeoCoverageRenderer(formalchemy.fields.FieldRenderer):
        def _get_value(self):
            form_regions = self._value # params
            if not form_regions:
                extras = self.field.parent.model.extras # db
                db_regions = extras.get(self.field.name, []) or []
                form_regions = schema_gov.GeoCoverageType.get_instance().db_to_form(db_regions)
            return form_regions

        def render(self, **kwargs):
            value = self._get_value()
            kwargs['size'] = '40'
            html = u''
            for i, region in enumerate(schema_gov.GeoCoverageType.get_instance().regions):
                region_str, region_munged = region
                id = '%s-%s' % (self.name, region_munged)
                checked = region_munged in value
                cb = literal(h.check_box(id, True, checked=checked, **kwargs))
                html += literal('<label for="%s">%s %s</label>') % (id, cb, region_str)
            return html

        def render_readonly(self, **kwargs):
            munged_regions = self._get_value()
            printable_region_names = schema_gov.GeoCoverageType.get_instance().munged_regions_to_printable_region_names(munged_regions)
            return common.field_readonly_renderer(self.field.key, printable_region_names)

        def _serialized_value(self):
            # interpret params like this:
            # 'Package--geographic_coverage-wales', u'True'
            # return list of covered regions
            covered_regions = []
            for region in schema_gov.GeoCoverageType.get_instance().regions_munged:
                if self.params.get(self.name + '-' + region, u'') == u'True':
                    covered_regions.append(region)
            return covered_regions

        def deserialize(self):
            return self._serialized_value()


# Setup the fieldset
def build_package_gov_form(is_admin=False):
    builder = package.build_package_form()

    # Extra fields
    builder.add_field(common.TextExtraField('resolution')) 
    builder.add_field(common.TextExtraField('abstract'))
    builder.add_field(common.DateExtraField('type'))
    builder.add_field(common.DateExtraField('locator'))
    builder.add_field(common.TextExtraField('service'))
    builder.add_field(common.TextExtraField('language'))
    builder.add_field(common.SuggestedTextExtraField('topic', options=schema_gov.geographic_granularity_options))
    builder.add_field(common.TextExtraField('subject'))
    builder.add_field(common.TextExtraField('vocabulary'))
    builder.add_field(common.TextExtraField('pubdate'))
    builder.add_field(common.TextExtraField('update_date'))
    builder.add_field(GeoLinkExtraField('geographic_link'))
    builder.add_field(GeoCoverageExtraField('geographic_coverage'))

    builder.add_field(common.SuggestedTextExtraField('temporal_granularity', options=schema_gov.temporal_granularity_options))

    builder.add_field(common.DateRangeExtraField('temporal_coverage'))


    builder.add_field(common.TextExtraField('create_date'))
    builder.add_field(common.TextExtraField('lineage'))
    builder.add_field(common.TextExtraField('specification'))
    builder.add_field(common.TextExtraField('conformity'))
    builder.add_field(common.TextExtraField('conditions'))
    builder.add_field(common.TextExtraField('restrictions'))
    builder.add_field(common.TextExtraField('foo'))

    # Options/settings
    
    # Layout
    field_groups = OrderedDict([
        (_('Basic information'), ['name', 'title', 
                                  'abstract', 'notes']),
        (_('Details'), ['create_date','pubdate', 'update_date',
                        'geographic_link',
                        'geographic_coverage',
                        'temporal_granularity', 'temporal_coverage',
                        'subject', 
                        'url','resolution']),
        (_('INSPIRE meta'), ['specification','conformity','service']),
        (_('Access'),['conditions','restrictions','license_id']), 
        (_('Resources'), ['resources']),
        (_('More details'), [
                             'author', 'author_email',
                             'maintainer', 'maintainer_email',
                             'tags' ]),
        ])
    if is_admin:
        field_groups['More details'].append('state')
    builder.set_displayed_fields(field_groups)
    return builder
    # Strings for i18n:
    [_('External reference'),  _('Date released'), _('Date updated'),
     _('Update frequency'), _('Geographic granularity'),
     _('Geographic coverage'), _('Temporal granularity'),
     _('Temporal coverage'), _('Categories'), _('National Statistic'),
     _('Precision'), _('Taxonomy URL'), _('Department'), _('Agency'), 
     ]

fieldsets = {} # fieldset cache

def get_fieldset(is_admin=False):
    '''Returns the standard fieldset
    '''
    if not fieldsets:
        # fill cache
        fieldsets['package_gov_fs'] = build_package_gov_form().get_fieldset()
        # admin blip here @@
        fieldsets['package_gov_fs_admin'] = build_package_gov_form(is_admin=False).get_fieldset()

    if is_admin:
        fs = fieldsets['package_gov_fs_admin']
    else:
        fs = fieldsets['package_gov_fs']
    return fs
