# -*- coding: utf-8 -*-
"""Provides atom feeds for the blog.

:Authors:
    - Bruce Kroeze
"""
"""
New BSD License
===============
Copyright (c) 2008, Bruce Kroeze http://solidsitesolutions.com

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of SolidSiteSolutions LLC, Zefamily LLC nor the names of its 
      contributors may be used to endorse or promote products derived from this 
      software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
__docformat__="restructuredtext"

from atompub import atom
from django.conf import settings
from django.core import urlresolvers
from banjo.common.util.files import url_join
from banjo.common.util.logs import warn_once

class PostSet(object):
    
    def __init__(self, blog, tag=None):
        self.blog = blog
        if cat and not cat is Category:
            try:
                cat = Category.objects.find(blog, cat, raises=True)
            except Category.DoesNotExist:
                cat = None
                
        self.category = cat
        if cat:
            self.posts = blog.posts_by_status(_PUBLISHED, False, None, category=cat)
        else:
            self.posts = blog.posts_by_status(_PUBLISHED, False, None)
        
class AtomTagFeed(atom.Feed):
    
    def __init__(self, request, blog):
        self.request = request
        self.blog = blog
        log.debug("AtomTagFeed for: %s", blog)
                
    def feed_authors(self, postset):
        for author in self.blog.authors.all():
            user = author.user
            yield {"name": user.get_full_name(), "email": user.email}
                
    def feed_categories(self, postset):
        if postset:
            if postset.category:
                cats = [postset.category,]
            else:
                cats = []
        else:
            cats = self.blog.categories.all()
            
        for cat in cats:
            log.debug('cat: %s', cat)
            caturl = cat.full_url(include_http=True)
            yield {'term' : cat.name, 'scheme' : caturl}

    def feed_icon(self, postset):        
        imgs = self.blog.images_by_tag('atom')
        if len(imgs) > 0:
            img = imgs[0].get_image_filename()
        else:
            warn_once(log, 'NO_FEED_ICON', 'no feed icon for blog: %s (add one by adding an image and tagging it "atom")', self.blog.name)
            img = url_join(settings.MEDIA_URL, 'blog/default/feed.png')
        return img

    def feed_id(self, postset):
        return self.blog.tag_uri
        
    def feed_links(self, postset):
        if postset and postset.category:
            blogurl = postset.category.full_url(include_http=True)
        else:
            blogurl = self.blog.full_url(include_http=True)
        
        return [{"rel": "alternate", "href": blogurl}]
        
    def feed_logo(self, postset):
        imgs = self.blog.images_by_tag('logo')
        if len(imgs) > 0:
            img = imgs[0].get_image_filename()
        else:
            warn_once(log, 'NO_FEED_LOGO', 'no logo for blog: %s (add one by adding an image and tagging it "logo")', self.blog.name)
            img = url_join(settings.MEDIA_URL, 'blog/default/logo.jpg')
        return img
        
    def feed_rights(self, postset):
        return self.blog.rights

    def feed_title(self, postset):
        return self.blog.name
    
    def feed_subtitle(self, postset):
        return self.blog.tagline
             
    def feed_updated(self, postset):
        if postset and postset.posts.count() > 0:
            return postset.posts.latest().update_date
        else:
            return self.blog.start_date

    def get_object(self, cats):
        cats = filter(lambda x: x, cats)
        log.debug('get_object: %s', cats)
        return PostSet(self.blog, cats)
        
    def items(self, postset):
        if postset:
            return postset.posts
        else:
            return self.blog.posts_by_status(_PUBLISHED, False, None)
        
    def item_id(self, post):
        return post.tag_uri
        
    def item_title(self, post):
        return post.headline
        
    def item_updated(self, post):
        return post.update_date
        
    def item_published(self, post):
        return post.pub_date
        
    def item_rights(self, post):
        return self.blog.rights
        
    def item_source(self, post):
        return {
            'id': post.tag_uri,
            'title' : post.headline,
            'updated' : post.update_date
            }
        
    def item_summary(self, post):
        return ("html", post.summary)
        
    def item_content(self, post):
        return ({ 
            'type' : 'html', 
            'xml:base' : 'http://' + self.blog.site.domain
            }, post.full_body)

    def item_categories(self, post):
        for cat in post.categories.all():
            log.debug('cat: %s', cat.key)
            if self.blog.sitedefault:
                caturl = urlresolvers.reverse('banjo_default_category_index', None, {'category' : cat.key})
            else:
                caturl = urlresolvers.reverse('banjo_category_index', None, {'blog' : self.blog.slug, 'category' : cat.key})
            yield {'term' : cat.name, 'scheme' : caturl}
        
    def item_links(self, post):
        link = post.get_absolute_url()
        return [{
            'rel' : 'alternate',
            'href' : link
        }]
        
    def item_authors(self, post):
        for author in post.authors.all():
            user = author.user
            yield {"name": user.get_full_name(), "email": user.email}
