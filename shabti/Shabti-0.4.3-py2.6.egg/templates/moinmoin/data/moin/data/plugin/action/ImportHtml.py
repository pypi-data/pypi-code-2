# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - ImportHtml action

"""

import mimetypes, string, sys, time, HTMLParser
from MoinMoin import config, user, util, wikiutil
from MoinMoin.util import web
from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
#from MoinMoin.util import MoinMoinNoFooter

#############################################################################
### Create parts of the Web interface
#############################################################################

def show_form(pagename, request):
    # request.http_headers()
    #wikiutil.send_title(request, "Import HTML as Markup")
    request.write(
"""
<form action="%(baseurl)s/%(pagename)s" method="POST" enctype="multipart/form-d\ata">
<input type="hidden" name="action" value="ImportHtml">
<input type="radio" name="do" value="markup">Show markup<br>
<input type="radio" name="do" value="wiki">Show as wiki page<br>
<input type="radio" name="do" value="import">Append to page<br>
URL: <input type="text" name="url" size="50">
<input type="submit" value="Get">
</form>
""" % {
        'baseurl': request.getBaseURL(),
        'pagename': wikiutil.quoteWikinameURL(pagename),
        })

    #wikiutil.send_footer(request, pagename, showpage=1)


def get_content(request):
    if request.form.has_key("url"):
        try:
            return urllib.urlopen(request.form["url"][0]).read()
        except IOError:
            return ""
    else:
        return ""

def get_parsed(request):
    # p = HTML2MoinMoin()
    # p.output = cStringIO.StringIO()
    # try:
    #     p.feed(get_content(request))
    #     p.close()
    # except:
    #     import traceback
    #     traceback.print_exc(None, p.output)
    # return p.output.getvalue()
    from MoinMoin.converter.text_html_text_moin_wiki import convert 
    return(convert(request, "Imported Page", get_content(request)))
    
def show_markup(pagename, request):
    request.http_headers(["Content-type: text/plain"])
    request.write(get_parsed(request))
    #raise MoinMoinNoFooter

def show_as_wiki_page(pagename, request):
    page = Page(pagename)
    page.set_raw_body(get_parsed(request), 1)
    page.send_page(request)

def append_to_page(pagename, request):
    page = PageEditor(request, pagename)
    page.set_raw_body(page.get_raw_body() + get_parsed(request))
    page.sendEditor()

def error_msg(pagename, request, msg):
    Page(pagename).send_page(request, msg=msg)


def execute(pagename, request):
    """ Main dispatcher for the 'ImportHtml' action.
    """
    _ = request.getText

    msg = None
    if not request.form.has_key('do'):
        show_form(pagename, request)
    elif request.form["do"][0] == "markup":
        show_markup(pagename, request)
    elif request.form["do"][0] == "wiki":
        show_as_wiki_page(pagename, request)
    elif request.form["do"][0] == "import":
        append_to_page(pagename, request)
    else:
        msg = _('<b>Unsupported action: %s</b>') % (request.form['do'][0],)
        
    if msg:
        error_msg(pagename, request, msg)


# def execute(pagename, request):
#     """
#     
#     """
#     # request.content_type = 'text/calendar'
#     # if hasattr(request, 'headers') and hasattr(request.headers, 'add'):#moin 1.9
#     #     request.headers.add('Content-Type: text/calendar')
#     #     request.headers.add('Content-Disposition', 'inline; filename="%s.ics"' %
#     #     pagename)
#     # else: # moin 1.8
#     #     request.emit_http_headers([                                                  
#     #         'Content-Type: text/calendar',
#     #         'Content-Disposition: inline; filename="%s.ics"' % pagename,
#     #     ])
#     
#     _ = request.getText
# 
#     msg = None
#     if not request.form.has_key('do'):
#         show_form(pagename, request)
#     elif request.form["do"][0] == "markup":
#         show_markup(pagename, request)
#     elif request.form["do"][0] == "wiki":
#         show_as_wiki_page(pagename, request)
#     elif request.form["do"][0] == "import":
#         append_to_page(pagename, request)
#     else:
#         msg = _('<b>Unsupported action: %s</b>') % (request.form['do'][0],)
#         
#     if msg:
#         error_msg(pagename, request, msg)
#     
#     request.write()
#     #request.close()




# from MoinMoin.Page import Page

# def execute(pagename, request):
#     """Execute the generation of the ics feed.
#     
#     Pagename must be the page where the month calendar is.
#     """
#     start_date = datetime.date.today() - START_RANGE
#     end_date = datetime.date.today() + END_RANGE
#     year_month_list = []
#     current_date = start_date.replace(day=1)
#     while current_date < end_date:
#         year_month_list.append((current_date.year, current_date.month))
#         firstday, monthlen = calendar.monthrange(current_date.year,
#                                                  current_date.month)
#         current_date += datetime.timedelta(days=monthlen)
#     
#     # Search for events and build the calendar
#     cal = VCalendar()
#     for year, month in year_month_list:
#         firstday, monthlen = calendar.monthrange(year, month)
#         for day in range(1, monthlen + 1):
#             link = "%s/%4d-%02d-%02d" % (pagename, year, month, day)
#             daypage = Page(request, link)
#             if daypage.exists() and request.user.may.read(link):
#                 #print "found :", link
#                 daycontent = daypage.get_raw_body()
#                 cal += extract_events_from_page(daycontent, year,month, day)
#     # Send the iCalendar file
#     request.content_type = 'text/calendar'
#     if hasattr(request, 'headers') and hasattr(request.headers, 'add'):#moin 1.9
#         request.headers.add('Content-Type: text/calendar')
#         request.headers.add('Content-Disposition', 'inline; filename="%s.ics"' %
#         pagename)
#     else: # moin 1.8
#         request.emit_http_headers([                                                  
#             'Content-Type: text/calendar',
#             'Content-Disposition: inline; filename="%s.ics"' % pagename,
#         ])
#     
#     request.write(str(cal))
#     #request.close()
