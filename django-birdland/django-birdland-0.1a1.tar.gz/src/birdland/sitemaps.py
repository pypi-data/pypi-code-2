from django.contrib.sitemaps import Sitemap
from birdland.models import Entry

class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Entry.objects.published()

    def lastmod(self, obj):
        return obj.publish
