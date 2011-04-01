from five import grok
from Products.ATContentTypes.interface.topic import IATTopic
import datetime
import json
import calendar

from Products.CMFCore.utils import getToolByName

from Products.PluginIndexes.interfaces import IDateIndex, IUniqueValueIndex

from zope import component as zca
from zope.interface import Interface
import traceback
from zope.app.schema.vocabulary import IVocabularyFactory

# for sanity check
EPOCH=datetime.datetime.fromtimestamp(1)

grok.templatedir('templates')


class ChartJson(grok.View):
    grok.name('chart_json')
    grok.context(IATTopic)

    def render(self):
        generator = self.request.get('t') or 'items-by-year'
        row_field = self.request.get('r')
        column_field = self.request.get('c')

        self.request.response.setHeader('Content-Type', 'application/json')
        stats = zca.getAdapter(self.context, IStatistics, generator)
        try:
            return json.dumps(stats.json(column_field, row_field))
        except Exception, e:
            traceback.print_exc()
            return json.dumps({'error': e.message})


class IStatistics(Interface):
    def json(): pass


class BaseDateStatistics(grok.Adapter):
    grok.implements(IStatistics)
    grok.context(IATTopic)
    grok.baseclass()

    def _query(self, row_field, **kwargs):

        # Sanity check, dont return anything older than EPOCH !!
        if (kwargs.has_key(row_field) and
            kwargs[row_field].has_key('query') and
            kwargs[row_field].has_key('range') and 
            kwargs[row_field]['range'] == 'min:max'):

            if kwargs[row_field]['query'][0] < EPOCH:
                kwargs[row_field]['query'] = (EPOCH,
                            kwargs[row_field]['query'][1])

            if kwargs[row_field]['query'][1] < EPOCH:
                kwargs[row_field]['query'] = (
                            kwargs[row_field]['query'][0], EPOCH)

        if not kwargs.has_key(row_field):
            kwargs[row_field] = {'query': EPOCH, 'range': 'min'}

        return self.context.queryCatalog(sort_on=row_field,
                                sort_order='ascending', **kwargs)

    def items_by_date(self, row_field, year, month=None, day=None, **params):
        
        start = datetime.datetime(year, month or 1, day or 1)

        if day is None:
            day = calendar.monthrange(year, month or 12)[1]

        end = datetime.datetime(year, month or 12, day)

        params[row_field] = {
            'query': (start, end),
            'range': 'min:max'
        }

        items = self._query(row_field, **params)

        return items

    def groups(self, column_field, row_field):
        if column_field is None:
            row_vocab = zca.getUtility(IVocabularyFactory,
                name='collective.googlevisualization.RowIndexesVocabulary')
            title = row_vocab(self.context).getTerm(row_field).title
            return [title]

        result = set()
        items = self._query(row_field)
        for item in items:
            val = getattr(item, column_field)
            if hasattr(val, '__iter__'):
                result.update(val)
            else:
                result.add(val)
        return result

    def json(self, column_field, row_field):
        columns = []
        columns.append({
            'type': 'string',
            'id': 'title',
            'label': 'Title'
        })

        for i in self.groups(column_field, row_field):
           columns.append({
               'type': 'number',
                'label': i
           })

        values = self._rows(column_field, row_field)

        return {
            'columns': columns,
            'values' : values
        }



class ItemsByYearStatistics(BaseDateStatistics):
    grok.name('items-by-year')

    def get_years(self, row_field):
        items = self._query(row_field)
        start = getattr(items[0], row_field).year() if items else 0
        end = getattr(items[-1], row_field).year() if items else 0
        return range(start, end + 1)

    def _rows(self, column_field, row_field):
        values = []

        for year in self.get_years(row_field):
            row = [str(year)]
            for group in self.groups(column_field, row_field):
                params = {}
                if column_field is not None:
                    params[column_field] = group
                items = self.items_by_date(row_field, year, **params)
                row.append(len(items))
            values.append(row)

        return values

class ItemsByMonthStatistics(BaseDateStatistics):
    grok.name('items-by-month')


    def get_months(self, row_field):
        items = self._query(row_field)
        first = getattr(items[0], row_field) if items else EPOCH
        final = getattr(items[-1], row_field) if items else EPOCH
        result = []

        first_year = first.year() if callable(first.year) else first.year
        final_year = final.year() if callable(final.year) else final.year
        first_month = first.month() if callable(first.month) else final.month
        final_month = final.month() if callable(final.month) else final.month

        if first_year < final_year:
            for month in range(first_month, 13):
                result.append((first_year, month))
            for year in range(first_year + 1, final_year):
                for month in range(1, 13):
                    result.append((year, month))
            for month in range(1, final_month + 1):
                result.append((final_year, month))

        elif first_year == final_year:
            for month in range(first_month, final_month + 1):
                result.append((first_year, month))
        
        return result

    def _rows(self, column_field, row_field):
        values = []

        for year, month in self.get_months(row_field):
            row = ['%s/%s' % (month, year)]
            for group in self.groups(column_field, row_field):
                params = {}
                if column_field is not None:
                    params[column_field] = group
                items = self.items_by_date(row_field, year, month, **params)
                row.append(len(items))
            values.append(row)

        return values



class ItemsByKeywordStatistics(grok.Adapter):
    grok.implements(IStatistics)
    grok.context(IATTopic)
    grok.name('items-by-keyword')

    def json(self, column_field, row_field):
        columns = []
        columns.append({
            'type': 'string',
            'id': 'title',
            'label': 'Title'
        })

        catalog = getToolByName(self.context, 'portal_catalog')

        row_keywords = set()
        columns_keywords = set()
        for item in self.context.queryCatalog():
            row_keywords.add(getattr(item, row_field)) if getattr(item,
                                                row_field) else None
            if column_field is None:
                row_vocab = zca.getUtility(IVocabularyFactory,
                    name='collective.googlevisualization.RowIndexesVocabulary')
                title = row_vocab(self.context).getTerm(row_field).title
                columns_keywords.add(title)
            else:
                columns_keywords.add(getattr(item, column_field)) if getattr(
                                    item, column_field) else None

        for c in columns_keywords:
            columns.append({
                'type': 'number',
                'label': c
            })

        values = []
        for r in row_keywords:
            row = [str(r)]
            for c in columns_keywords:
                params = {row_field: r}
                if column_field is not None:
                    params[column_field] = c
                row.append(len(self.context.queryCatalog(**params)))
            values.append(row)

        return {
            'columns': columns,
            'values': values
        }
            
