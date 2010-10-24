from redsolutioncms.make import BaseMake
from redsolutioncms.models import CMSSettings

class Make(BaseMake):
    def make(self):
        super(Make, self).make()
        cms_settings = CMSSettings.objects.get_settings()
        cms_settings.render_to('settings.py', 'chunks/redsolutioncms/settings.pyt')
        cms_settings.render_to(['..', 'templates', 'base_chunks.html'],
            'chunks/redsolutioncms/base_chunks.html', {
        }, 'w')
        cms_settings.render_to('urls.py', 'chunks/redsolutioncms/urls.pyt')
        cms_settings.render_to(['..', 'templates', 'robots.txt'],
            'chunks/redsolutioncms/robots.txt', {}, 'w')
        # render initial data fixture
        cms_settings.render_to(['..', 'fixtures', 'initial_data.json'],
            'chunks/redsolutioncms/initial_data.json')
        cms_settings.base_template = 'base_chunks.html'
        cms_settings.save()

make = Make()

