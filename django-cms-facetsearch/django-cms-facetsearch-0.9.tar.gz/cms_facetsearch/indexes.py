from django.conf import settings

from django.utils.encoding import force_unicode
from django.utils.html import strip_tags
from django.utils.translation import get_language, activate

from haystack import indexes

from cms.models.pluginmodel import CMSPlugin

class TranslationIndex(indexes.SearchIndex):
    
    language = indexes.CharField(faceted=True)
    
    def get_language(self, obj):
        return obj.language
        
    def prepare_translated(self, obj, language):
        return {}
        
    def prepare(self, obj):
        current_languge = get_language()
        language = self.get_language(obj)
        try:
            activate(language)
            self.prepared_data = super(TranslationIndex, self).prepare(obj)
            data = self.prepare_translated(obj, language)
            self.prepared_data.update(data)
            return self.prepared_data
        finally:
            activate(current_languge)
            
class PluginIndex(TranslationIndex):
    
    text = indexes.CharField(document=True, use_template=False)

    def get_placeholders(self, obj, language): 
        raise NotImplemented
    
    def get_plugins(self, obj, language):
        placeholders = self.get_placeholders(obj, language)
        return CMSPlugin.objects.filter(language=language, placeholder__in=placeholders)	
                
    def prepare_translated(self, obj, language):
        plugins = self.get_plugins(obj, language)
        data = {'language': language}
        text = ''
        for plugin in plugins:
            instance, _ = plugin.get_plugin_instance()
            if hasattr(instance, 'search_fields'):
                text += u''.join(force_unicode(strip_tags(getattr(instance, field, ''))) for field in instance.search_fields)
            if getattr(instance, 'search_fulltext', False):
                text += strip_tags(instance.render_plugin())
        data['text'] = text
        return data
        
 