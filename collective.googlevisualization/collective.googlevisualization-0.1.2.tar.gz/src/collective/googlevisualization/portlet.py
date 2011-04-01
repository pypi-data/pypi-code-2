from zope.interface import implements,alsoProvides
from zope.component import adapts,getAdapter,getAdapters

from plone.app.portlets.portlets import base
from plone.portlet.collection import collection
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from zope import schema
from zope.formlib import form
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.schema.vocabulary import SimpleVocabulary,SimpleTerm
from zope.app.schema.vocabulary import IVocabularyFactory

import hashlib
import json

# XXX Temporary hack to fix (no value) validation issue
from zope.app.form.browser.widget import SimpleInputWidget
_orig_getFormInput = SimpleInputWidget._getFormInput
def _getFormInput(self):
    value = _orig_getFormInput(self)
    if getattr(self, '_messageNoValue', None):
        if value == self.translate(self._messageNoValue):
            return self._missing
    return value
SimpleInputWidget._getFormInput = _getFormInput

# XXX: make these configurable somewhere
CHART_TYPES=[
    ('ColumnChart', 'Bar Chart'),
    ('BarChart', 'Horizontal Bar Chart'),
    ('PieChart', 'Pie Chart'),
    ('AreaChart', 'Area Chart'),
    ('Table', 'Table')
]

# XXX: make this acquired automatically from adapter registry
DATE_TYPES=[
#    ('items-by-keyword', 'By Keyword'),
    ('items-by-year', 'By Year'),
    ('items-by-month', 'By Month')
]

# XXX: need a control panel to control these
COLUMN_INDEXES=[
    ('Subject', 'Keyword'),
    ('Type', 'Item Type'),
    ('Creator', 'Creator'),
    ('review_state', 'Publication State')
]

DATE_INDEXES=[
    ('created', 'Creation Date'),
    ('effective', 'Effective Date'),
    ('expires', 'Expiry Date'),
    ('start', 'Start Date'),
    ('end', 'End Date'),
    ('modified', 'Modification Date')
]

ROW_INDEXES=DATE_INDEXES + COLUMN_INDEXES

def chart_config(json_url, column_field, row_field,
                stats_type, chart_type, height=None, width=None):

    js = '''

    var gvisualization_chart_settings = %s
    '''

    settings = {
        'type': chart_type,
        'source': {
            'url': json_url,
            'data': {'r': row_field,
                    't': stats_type}
        },
        'options': {}
    }

    if column_field is not None:
        settings['source']['data']['c'] = column_field

    if height is not None:
        settings['options']['height'] = height
    if width is not None:
        settings['options']['width'] = width

    return js % json.dumps(settings)


def ChartTypeVocabulary(context):
    terms = []
    for t, v in CHART_TYPES:
        terms.append(SimpleVocabulary.createTerm(t, t, v))
    return SimpleVocabulary(terms)
alsoProvides(ChartTypeVocabulary, IVocabularyFactory)

def DateTypeVocabulary(context):
    terms = []
    for t, v in DATE_TYPES:
        terms.append(SimpleVocabulary.createTerm(t, t, v))
    return SimpleVocabulary(terms)
alsoProvides(DateTypeVocabulary, IVocabularyFactory)

def RowIndexesVocabulary(context):
    terms = []
    for t, v in ROW_INDEXES:
        terms.append(SimpleVocabulary.createTerm(t, t, v))
    return SimpleVocabulary(terms)
alsoProvides(RowIndexesVocabulary, IVocabularyFactory)

def ColumnIndexesVocabulary(context):
    terms = []
    for t, v in COLUMN_INDEXES:
        terms.append(SimpleVocabulary.createTerm(t, t, v))
    return SimpleVocabulary(terms)
alsoProvides(ColumnIndexesVocabulary, IVocabularyFactory)


class ICollectionChart(collection.ICollectionPortlet):
    chart_type = schema.Choice(title=u'Chart Type',
                                default='ColumnChart',
                                required=True,
            vocabulary='collective.googlevisualization.ChartTypeVocabulary')

    row_index = schema.Choice(title=u'Row Values',
                            required=True,
            vocabulary='collective.googlevisualization.RowIndexesVocabulary')

    column_index = schema.Choice(title=u'Column Values',
                            required=False,
                            default=None,
          vocabulary='collective.googlevisualization.ColumnIndexesVocabulary')

    date_mode = schema.Choice(title=u'Date Rendering Mode',
                            required=True,
                            default='items-by-year',
          vocabulary='collective.googlevisualization.DateTypeVocabulary')
    

    height = schema.Int(title=u'Height',
                        required=False,
                        default=180)

    width = schema.Int(title=u'Width',
                        required=False,
                        default=180)
class Assignment(collection.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ICollectionChart)

    def __init__(self, header=u"", target_collection=None, limit=None,
                random=False, show_more=True, show_dates=False,
                chart_type='ColumnChart', row_index='created', 
                column_index='Type', date_mode='items-by-year',
                width=180, height=180):
        super(Assignment, self).__init__(header, target_collection, limit, 
                                        random, show_more, show_dates)
        self.chart_type = chart_type
        self.row_index = row_index
        self.column_index = column_index
        self.date_mode = date_mode
        self.height = height
        self.width = width
        

class Renderer(collection.Renderer):
    _template = ViewPageTemplateFile('portlet.pt')

    render = _template

    def portlethash(self):
        # FIXME: need a better hashing
        return hashlib.md5(''.join([self.data.id,
                                    self.manager.__name__,
                                    self.collection_url(), 
                                    self.context.absolute_url()])
                ).hexdigest()

    def js(self, selector):
        chart_type = self.data.chart_type
        column_field = self.data.column_index
        row_field = self.data.row_index
        height = self.data.height
        width = self.data.width

        if row_field in [i[0] for i in DATE_INDEXES]:
            stats_type = self.data.date_mode
        else:
            stats_type = 'items-by-keyword'
        url = "%s/chart_json" % self.collection_url()

        config = chart_config(url, column_field, row_field,
                                stats_type, chart_type, height=height,
                                width=width)

        return '''
            $(document).ready(function () {
                %s
                $('%s').gvisualization(gvisualization_chart_settings);
            });
        ''' % (config, selector)


class AddForm(collection.AddForm):
    form_fields = form.Fields(ICollectionChart).omit('limit', 'show_dates',
                                                    'show_more', 'random')
    form_fields['target_collection'].custom_widget = UberSelectionWidget

    def create(self, data):
        return Assignment(**data)

class EditForm(collection.EditForm):
    form_fields = form.Fields(ICollectionChart).omit('limit', 'show_dates',
                                                    'show_more', 'random')
    form_fields['target_collection'].custom_widget = UberSelectionWidget

