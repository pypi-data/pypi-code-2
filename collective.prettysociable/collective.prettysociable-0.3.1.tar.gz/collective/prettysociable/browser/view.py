from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class JavaScript(BrowserView):

    @property
    def prettysociable_properties(self):
        properties_tool = getToolByName(self.context, 'portal_properties')
        return getattr(properties_tool, 'prettysociable_properties', None)

    def __call__(self, request=None, response=None):
        """Returns global configuration for prettySociable taken from
           portal_properties."""
        self.request.response.setHeader("Content-type", "text/javascript")

        js = """jq(document).ready(function(){ """

        # Use prettySociable for links. To use your custom JS, disable
        # 'enable_default' in prettysociable_properties.
        if getattr(self.prettysociable_properties, 'enable_default', True):
            js += """// add rel tag for all links with class 'prettySociable'
                    jq("a.prettySociable").each(function() {
                        jq(this).attr({'href': this.href});
                        var title = jq(this).attr('title');
                        if (title == '') {
                            title = jq(this).text();
                        }
                        jq(this).attr({"rel": "prettySociable;title:" + title + ";excerpt:;"});
                    });
                  """

        # Use prettySociable for the first heading (h1) on each page
        # (permalink). To add your own JS for this, disable 'enable_h1'
        # in prettyscociable_properties.
        if getattr(self.prettysociable_properties, 'enable_h1', True):
            js += """// add link to h1 (acts as permalink)
                    var thisURL = jQuery.url.attr("source");
                    jq("h1.documentFirstHeading").wrapInner('<a href="' + thisURL + '" rel="prettySociable"></a>');
                  """

        # Neccessary prettySociable JS code.
        js += """jq.prettySociable({
                    animationSpeed: '%(speed)s', /* fast/slow/normal */
                    opacity: %(opacity)s, /* Value between 0 and 1 */
                    share_label: 'Drag to share', /* Text displayed when a user rollover an item */
                    share_on_label: 'Share on ', /* Text displayed when a user rollover a website to share */
                    hideflash: %(hide_flash)s, /* Hides all the flash object on a page, set to TRUE if flash appears over prettySociable */
                    hover_padding: %(hover_padding)s,
                    websites: {
                        facebook: {
                            'active': %(facebook_active)s,
                            'encode': %(facebook_encode)s, // If sharing is not working, try to turn to false
                            'title': 'Facebook',
                            'url': 'http://www.facebook.com/share.php?u=',
                            'icon': '++resource++prettySociable.facebook.png',
                            'sizes': {'width': %(image_width)s, 'height': %(image_height)s}
                        },
                        twitter: {
                            'active': %(twitter_active)s,
                            'encode': %(twitter_encode)s, // If sharing is not working, try to turn to false
                            'title': 'Twitter',
                            'url': 'http://twitter.com/home?status=',
                            'icon': '++resource++prettySociable.twitter.png',
                            'sizes': {'width': %(image_width)s, 'height': %(image_height)s}
                        },
                        delicious: {
                            'active': %(delicious_active)s,
                            'encode': %(delicious_encode)s, // If sharing is not working, try to turn to false
                            'title': 'Delicious',
                            'url': 'http://del.icio.us/post?url=',
                            'icon': '++resource++prettySociable.delicious.png',
                            'sizes': {'width': %(image_width)s, 'height': %(image_height)s}
                        },
                        digg: {
                            'active': %(digg_active)s,
                            'encode': %(digg_encode)s, // If sharing is not working, try to turn to false
                            'title': 'Digg',
                            'url': 'http://digg.com/submit?phase=2&url=',
                            'icon': '++resource++prettySociable.digg.png',
                            'sizes': {'width': %(image_width)s, 'height': %(image_height)s}
                        },
                        linkedin: {
                            'active': %(linkedin_active)s,
                            'encode': %(linkedin_encode)s, // If sharing is not working, try to turn to false
                            'title': 'LinkedIn',
                            'url': 'http://www.linkedin.com/shareArticle?mini=true&ro=true&url=',
                            'icon': '++resource++prettySociable.linkedin.png',
                            'sizes': {'width': %(image_width)s, 'height': %(image_height)s}
                        },
                        reddit: {
                            'active': %(reddit_active)s,
                            'encode': %(reddit_encode)s, // If sharing is not working, try to turn to false
                            'title': 'Reddit',
                            'url': 'http://reddit.com/submit?url=',
                            'icon': '++resource++prettySociable.reddit.png',
                            'sizes': {'width': %(image_width)s, 'height': %(image_height)s}
                        },
                        stumbleupon: {
                            'active': %(stumbleupon_active)s,
                            'encode': %(stumbleupon_encode)s, // If sharing is not working, try to turn to false
                            'title': 'StumbleUpon',
                            'url': 'http://stumbleupon.com/submit?url=',
                            'icon': '++resource++prettySociable.stumbleupon.png',
                            'sizes': {'width': %(image_width)s, 'height': %(image_height)s}
                        },
                        tumblr: {
                            'active': %(tumblr_active)s,
                            'encode': %(tumblr_encode)s, // If sharing is not working, try to turn to false
                            'title': 'tumblr',
                            'url': 'http://www.tumblr.com/share?v=3&u=',
                            'icon': '++resource++prettySociable.tumblr.png',
                            'sizes': {'width': %(image_width)s, 'height': %(image_height)s}
                        }
                    }
                });
            });
            """ % dict(
                    speed = getattr(self.prettysociable_properties, 'speed', 'normal'),
                    opacity = getattr(self.prettysociable_properties, 'opacity', 0.80),
                    hide_flash = getattr(self.prettysociable_properties, 'hide_flash', True) and 'true' or 'false',
                    hover_padding = getattr(self.prettysociable_properties, 'hover_padding', 0),
                    image_height = getattr(self.prettysociable_properties, 'image_height', 70),
                    image_width = getattr(self.prettysociable_properties, 'image_width', 70),

                    facebook_active = getattr(self.prettysociable_properties, 'facebook_active', True) and 'true' or 'false',
                    facebook_encode = getattr(self.prettysociable_properties, 'facebook_encode', True) and 'true' or 'false',
                    twitter_active = getattr(self.prettysociable_properties, 'twitter_active', True) and 'true' or 'false',
                    twitter_encode = getattr(self.prettysociable_properties, 'twitter_encode', True) and 'true' or 'false',
                    delicious_active = getattr(self.prettysociable_properties, 'delicious_active', True) and 'true' or 'false',
                    delicious_encode = getattr(self.prettysociable_properties, 'delicious_encode', True) and 'true' or 'false',
                    digg_active = getattr(self.prettysociable_properties, 'digg_active', True) and 'true' or 'false',
                    digg_encode = getattr(self.prettysociable_properties, 'digg_encode', True) and 'true' or 'false',
                    linkedin_active = getattr(self.prettysociable_properties, 'linkedin_active', True) and 'true' or 'false',
                    linkedin_encode = getattr(self.prettysociable_properties, 'linkedin_encode', True) and 'true' or 'false',
                    reddit_active = getattr(self.prettysociable_properties, 'reddit_active', True) and 'true' or 'false',
                    reddit_encode = getattr(self.prettysociable_properties, 'reddit_encode', True) and 'true' or 'false',
                    stumbleupon_active = getattr(self.prettysociable_properties, 'stumbleupon_active', True) and 'true' or 'false',
                    stumbleupon_encode = getattr(self.prettysociable_properties, 'stumbleupon_encode', True) and 'true' or 'false',
                    tumblr_active = getattr(self.prettysociable_properties, 'tumblr_active', True) and 'true' or 'false',
                    tumblr_encode = getattr(self.prettysociable_properties, 'tumblr_encode', True) and 'true' or 'false',
              )
        
        return js
