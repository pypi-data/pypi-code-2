from haystack import indexes, site
from cms_facetsearch.indexes import PluginIndex
from cmsplugin_blog.models import EntryTitle

class EntryTitleIndex(PluginIndex):
    title = indexes.CharField(model_attr='title')
    url = indexes.CharField(stored=True)

    def get_placeholders(self, obj, language):
        return obj.entry.placeholders.all()
        
    def prepare_translated(self, obj, language):
        data = super(EntryTitleIndex, self).prepare_translated(obj, language)
        data['url'] = obj.get_absolute_url()
        return data

site.register(EntryTitle, EntryTitleIndex)