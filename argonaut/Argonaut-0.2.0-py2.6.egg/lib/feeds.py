import argonaut.lib.helpers as h

XML_BEGIN = '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>'+h.config.get('rss_title')+'</title><description>'+h.config.get('rss_title')+'</description><link>'+h.config.get('site_url')+'</link>'
XML_END = '</channel></rss>'

def update():
    posts = h.post.get_many(amount=10, active_only=True, order='desc')
    xml_file = open(h.config.get('rss_path')+h.config.get('rss_filename'),'w')
    xml_file.write(XML_BEGIN+'\n')
    for p in posts:
        xml_file.write("<item>\n")
        subject = p.subject.replace("&#39;","'").replace('&','&#38;').replace('<','&#60;')
        link = h.config.get('site_url')+h.escape(h.url('blog_post', id=p.id, subject=h.urlify(p.subject)))
        xml_file.write('<title><a href="'+link.encode('utf8')+'">'+subject.encode('utf8')+'</a></title>\n')
        tags = h.tag_post.get_tags(p.id)
        tags_str = ''
        for tag in tags:
            tags_str += tag.name
        xml_file.write("<category>"+tags_str.encode('utf8')+"</category>\n");
        posted = p.posted.strftime('%a, %d %b %Y %H:%M:%S +0200')
        xml_file.write("<pubDate>"+posted+"</pubDate>\n")
        xml_file.write("<description><![CDATA["+p.body.encode('utf8')+"]]></description>\n")
        xml_file.write("<link>"+link.encode('utf8')+"</link>\n")
        xml_file.write("</item>")
        xml_file.write("\n")
    xml_file.write("\n")
    xml_file.write(XML_END)
    xml_file.close()
