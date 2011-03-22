"""
    MoinMoin - EmbedWikiPage a macro to embed a wiki page from a different wiki
    @license: GNU GPL, see COPYING for details.

    PURPOSE:
        This macro is used to embed a wiki page into the current wikipage.
	It is possible to embed local pages as well as external wiki pages.

	if a WikiName is detected the name is translated into a link to the original page.
	On some circumstances a WikiName is not detected, see RESTRICTIONS.

        The page is embedded temporary and you get at the end a link to edit the original page.

	At this stage it could be used to embed single pages e.g. macro explanaitions from moinmoin

    CALLING SEQUENCE:
       [[EmbedWikiPage(site,name)]]


    INPUTS:
       site: the URL of the wiki where the page is on
       name: the wikiname of the page

    EXAMPLE:
       [[EmbedWikiPage(http://moinmoin.wikiwikiweb.de:8000/,ProcessorMarket/sctable)]]

    PROCEDURE:
      * Editing of an embedded page is always editing the original page.
      * wiki:, wiki:/ or [" "] page and normal !WikiName links are followed to their original locations
      * attachments are embedded

      Please remove the version number from the routine name!

    RESTRICTIONS:
      * at the moment it follows nearly all wiki links

      I have a simple mechanism to detect wiki:, wiki:/ or ["HOWTO"] and normal !WikiName pagelinks

      At the moment I don't find !WikiName which are inserted into tabulars and macros.

      Later on it would be fine to use the icon of the page (favicon)
      to show where are the links from.

    MODIFICATION:
       @copyright: 2004-09-26 by Reimar Bauer (R.Bauer@fz-juelich.de) EmbedWikiPage-1.2.3-1
       2004-09-28: RB 1.2.3-2 !WikiName is now supported (some cases are missing)
       2004-09-28: RB 1.2.3-3 !WikiName rules extended
       2004-10-16: RB 1.2.3-4 trailing space in site or name ignored
       2004-12-20: RB 1.3.1-1 adopted to new wiki syntax

    DISCUSSION:




"""
import string, codecs, os, urllib
from MoinMoin.parser import text_moin_wiki as wiki
from MoinMoin import wikiutil
from MoinMoin import config

def fetchfile(urlopener, url):
#Copyright (c) 2002-2003  Gustavo Niemeyer <niemeyer@conectiva.com>
# adopted by Reimar Bauer
    geturl = url+"?action=raw"
    filename, headers = urlopener.retrieve(geturl)
    return filename

def get_urlopener(moinurl):
#Copyright (c) 2002-2003  Gustavo Niemeyer <niemeyer@conectiva.com>
# adopted by Reimar Bauer
    urlopener = urllib.URLopener()
    proxy = os.environ.get("http_proxy")
    if proxy:
        urlopener.proxies.update({"http": proxy})
    return urlopener


def execute(macro, text):

    request=macro.request
    formatter=macro.formatter

    if text:
      args=text.split(',')
    else:
      args=[]
    number_args=len(args)
    if number_args < 2:
      return macro.formatter.sysmsg('Not enough arguments to EmbedWikiPage macro')


    site=wikiutil.escape(string.join(string.strip(args[0]),''), quote=1)
    name=wikiutil.escape(string.join(string.strip(args[1]),''), quote=1)

    url="%(site)s%(name)s" %{
          "site": site,
	  "name": name
	}

    if (name.find("/") > -1):
       wikiname=(name.split('/'))[0]
    else:
       wikiname=name

    urlopener = get_urlopener(url)
    moinfile = fetchfile(urlopener, url)


    file = codecs.open(moinfile, 'rb', config.charset)
    txt = file.read()
    file.close()
    words=txt.split(" ")
    i=0
    for item in words:
      if (item.find('attachment:') > -1):
          words[i]=string.replace(words[i],"attachment:",site+name+'?action=AttachFile&do=get&target=')
      if (item.find('/') == 0):
         words[i]=string.replace(words[i],string.replace(item,'.',''),' ['+site+name+string.replace(item,'.','')+' '+item+']')

      if (item.find('wiki:/') > -1):
          s=string.replace(item,'_','(5f)')
          words[i]=string.replace(words[i],item,s)
          words[i]=string.replace(words[i],"wiki:/",site+name+'/')

      if (item.find('wiki:') > -1):
          s=string.replace(item,'_','(5f)')
          words[i]=string.replace(words[i],item,s)
          words[i]=string.replace(words[i],"wiki:",site)
      if (item.find('[') > -1 ):
         if (item[0] == '['):
            if (item[1] == '"'):
                w=item[2:]
                pos=w.find('"')
                w=w[0:pos]
                pos=item.find(']')
                w=w[0:pos]
		if ((len(w)) < len(item)) :
		    further=item[(pos+1):]
		else:
		    further=""
                words[i]=string.replace(words[i],item,'['+site+wikiname+'/'+w+' '+w+']')+further
      test=item
      if (test.find('.') > -1):
          test=string.replace(test,'.','')
      if (test.find(',') > -1):
          test=string.replace(test,',','')
      if (test.find('!') > 0):
          test=string.replace(test,'!','')
      if (test.find(';') > -1):
          test=string.replace(test,';','')

      if wikiutil.isStrictWikiname(test):
#         if (item.find('_') > -1):
#             words[i]=string.replace(words[i],'_','(5f)')
         words[i]=string.replace(words[i],test,' ['+site+wikiname+'/'+test+' '+test+']')




      i=i+1

    txt=string.join(words," ")

    request.write('<HR width=50%>')

    wikiizer = wiki.Parser(string.join(txt,""),request)
    wikiizer.format(formatter)

    edit_url=url+'?action=edit'

    edit_icon=request.theme.make_icon("edit")

    request.write('<HR>')
    cmd="<a title=%(edit_url)s href=%(edit_url)s > %(edit_icon)s   %(txt)s</a>" % {
      "edit_url":'"'+edit_url+'"',
      "edit_icon":edit_icon,
      "txt":'Edit embedded page '+name+' on '+site
      }


    request.write(cmd)
    return ""





