#!/usr/bin/python
# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2011 - 2011 by Eike Welk                                #
#    eike.welk@gmx.net                                                     #
#                                                                          #
#    License: GPL                                                          #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

'''
Analysis program for prices on Ebay; for use in conjunction with JBidwatcher.

The program creates price vs. time diagrams, with moving median price over a
configurable period of time. It is a command line program, but the graph is
displayed in an interactive graph window. There the graph can be scaled, moved 
and saved as an image.

Look at the example image `Nikon SB.png`.
'''

#Configure Python interpreter
from __future__ import division
from __future__ import absolute_import

#Import the libraries we use
import sys
import os
import csv
import datetime
import fnmatch
import optparse
import xml.etree.ElementTree as et
from collections import namedtuple
from itertools import chain
from operator import attrgetter
from numpy import nan, array, ones, zeros_like, median, isfinite
from matplotlib.pyplot import plot_date, figure, legend, title, show
import matplotlib.dates
import dateutil
#import pprint



#Program version for help and error messages
PROGRAM_VERSION = '0.1.5'



class UserError(Exception):
    '''
    Exception for regular fatal program error, that was cause by faulty user
    input. As opposed to a program internal error.
    '''



BaseAuction = namedtuple('Auction', 'id, end_time, '
                                    'item_price, shipping_price, currency,'
                                    'comment, category,'
                                    'complete, bid_count')
class Auction(BaseAuction):
    '''
    Represents one Ebay auction.

    Inherits from a named tuple for the generated __repr__ and __init__
    functions.
    '''
    @property
    def total_price(self):
        return self.item_price + self.shipping_price



#Represents the user's intentions. Correlates to the command line options.
Task = namedtuple('Task', 'action, input_file, output_img, show_window, '
                          'cats_in, cats_ex, group_cats, '
                          'comms_in, comms_ex, group_comms, '
                          'column_name, avg_length, chart_title, long_output')



#def find_xml_file():
#    '''
#    Find the most recent version of JBidwatcher's auctions.xml file.
#    '''
#    #Find JBidwatcher's data directory
#    jbidwatcher_dir = os.path.expanduser('~/.jbidwatcher')
#
#    #Get list of XML files from JBidwatcher
#    all_files = os.listdir(jbidwatcher_dir)
#    auct_files = fnmatch.filter(all_files, 'auctions*.xml')
#
#    #find the newest XML file
#    max_mtime = 0
#    newest_file = None
#    for xml_name in auct_files:
#        xml_path = os.path.join(jbidwatcher_dir, xml_name)
#        #os.path.isfile(xml_path)
#        mtime = os.path.getmtime(xml_path)
#        if mtime > max_mtime:
#            max_mtime = mtime
#            newest_file = xml_path
#
#    return newest_file



def find_xml_file():
    '''
    Find JBidwatcher's auctions.xml file.

    This is always the most recent of the several 'auctions*.xml' files in
    the directory '~/.jbidwatcher/'.
    '''
    xml_file = os.path.expanduser('~/.jbidwatcher/auctions.xml')
    return xml_file



def interpret_xml(xml_text):
    '''
    Read XML string from JBidwatcher and return a list of Auction objects

    Documentation on Elementtree:
    http://docs.python.org/library/xml.etree.elementtree.html
    http://effbot.org/zone/element-index.htm

    '''
    epoch2num = matplotlib.dates.epoch2num
    auction_list = []
    root_xml = et.fromstring(xml_text)
    server_xml = root_xml.find('auctions/server/')
    for auct_xml in server_xml:
        info_xml = auct_xml.find('info')
        auction_id = auct_xml.get('id')
        #Unix time-stamp (in ms) is converted to days since CE
        end_time = epoch2num(int(info_xml.find('end').text) / 1000)
        item_price = float(info_xml.find('currently').get('price'))
        shipping_xml = info_xml.find('shipping')
        shipping_price = float(shipping_xml.get('price')) \
                         if shipping_xml is not None else nan
        currency = info_xml.find('currently').get('currency')
        comment_xml = auct_xml.find('comment')
        comment = comment_xml.text if comment_xml is not None else ''
        category = auct_xml.find('category').text
        complete = True if auct_xml.find('complete') is not None else False
        bid_count = int(info_xml.find('bidcount').text)

        auction = Auction(auction_id, end_time,
                          item_price, shipping_price, currency,
                          comment, category, complete, bid_count)
        auction_list.append(auction)

#        #Investigate: Are 'auct_xml/shipping' and 'auct_xml/info_xml/shipping'
#        #always equal? It seems so.
#        shipping_xml2 = auct_xml.find('shipping')
#        shipping_price2 = float(shipping_xml2.get('price')) \
#                          if shipping_xml is not None else nan
#        if shipping_price2 != shipping_price:
#            print 'Warning: shipping_price2 != shipping_price'
#            print 'shipping_price2 = {s2} shipping_price = {s}'\
#                  .format(s2=shipping_price2, s=shipping_price)

        #print auction
        #et.dump(auct_xml); print '\n\n'
    return auction_list



def interpret_csv(csv_text):
    '''
    Interpret a text in CSV format

    RETURNS
    -------
        list[Auction]
    '''
    #remove comments and blank lines
    lines_1 = csv_text.split('\n')
    lines_2 = []
    for line_dict in lines_1:
        line_dict = line_dict.strip()
        if line_dict == '':
            # remove blank line_dict
            continue
        elif line_dict.startswith('#'):
            # remove comment line_dict
            continue
        lines_2.append(line_dict)

    #interpret lines that contain CSV data,
    auct_list = []
    reader = csv.DictReader(lines_2, delimiter=',', quotechar='"',
                            skipinitialspace=True)
    for line_dict in reader:
        auct_id = line_dict['Number']
        end_time = convert_date_str(line_dict['Time left'])
        complete = True if end_time >= 0 else False
        comment = line_dict['Comment']
        category = ''

        #One of these three values can be missing: total = current + shipping
        total = line_dict.get('Total', None)
        current = line_dict.get('Current', None)
        shipping = line_dict.get('Shipping', None)
        #compute missing value if necessary
        #Additionally we get the currency symbol and bid count 
        #from part of a price string
        if current and shipping:
            item_price, currency_sym, bid_count = convert_price_str(current)
            shipping_price, _, _ = convert_price_str(shipping)
        elif total and current:
            item_price, currency_sym, bid_count = convert_price_str(current)
            total_price, _, _ = convert_price_str(total)
            shipping_price = total_price - item_price
        elif total and shipping:
            total_price, currency_sym, _ = convert_price_str(total)
            shipping_price, _, _ = convert_price_str(shipping)
            item_price = total_price - shipping_price
            bid_count = 1
        else:
            raise UserError('CSV file is missing necessary price information! \n'
                            'Two columns from "Total, Current, Shipping" '
                            'must be present.')
            
        bid_count = 1 if bid_count is None else bid_count
        
        #create new auction and append it to result list
        new_auct = Auction(auct_id, end_time,
                           item_price, shipping_price, currency_sym,
                           comment, category, complete, bid_count)
        auct_list.append(new_auct)

    return auct_list



def convert_price_str(in_str):
    '''
    Convert strings that denote amounts of money into the amount (float)
    the currency symbol, and the number of bids.

    The function understands three formats: "€65.00 (FP)", "€65.00 (13)", "€68.90"

    Returns
    -------

    tuple[float, str]
    A tuple containing
        - the amount : float
        - the currency symbol : str
        - the number of bids: str, NoneType
              None is returned for the number of bids, if it can not be 
              determined.
    '''
    #Remove leading and trailing white space
    in_str = in_str.strip()
    #To the left of space is amount of money, to the right is number of bids
    money_bids = in_str.split(' ')
    if len(money_bids) == 2:
        money, bids = money_bids
    else:
        money, bids = money_bids[0], None
    #remove numeric part on the right. Remainder is currency symbol
    sym = money.rstrip('1234567890.,')
    #remove currency symbol on left, to get number
    #and remove comma (used as thousands separator
    num = float(money[len(sym):].replace(',',''))
    #Remove the brackets, and convert to an integer. Yields number of bids.
    try:
        nbids = int(bids.strip('()')) 
    except ValueError:
        nbids = None
    except AttributeError:
        nbids = None
        
    return num, sym, nbids



def convert_date_str(date_time_str):
    '''
    Convert date strings into (float) days. The hours become decimal places.

    Understands two formats:
    "18-Mar-10 18:21:58 CET"
        Converted to days since CE (1-Jan-0001)
        18-Mar-10 is day 733849.723588

    " 6d,  2h"
        Unfinished auctions are converted to -1
    '''
    try:
        #date = datetime.datetime.strptime(date_str, '%d-%b-%y')
        date = dateutil.parser.parse(date_time_str)
        num = matplotlib.dates.date2num(date)
        #print "Date: {0}, num: {1}".format(date.strftime('%d.%m.%Y'), num)
    except ValueError:
        num = -1
        #print "Could not convert date! num: {0}".format(num)

    return num



#def convert_prod_str(pname_comment):
#    '''
#    Convert product name to a standard format.
#
#    The product name is in the comment field. It may be augmented by a real
#    comment which must be removed for further processing.
#    The product name is to the left of a "|" character, if any
#    '''
#    pname = pname_comment.split('|')[0]
#    return pname.strip()



def get_category(auction):
    '''Key function for `group_auctions`. Accesses the category/tab.'''
    return auction.category

def get_prod_comment(auction):
    '''
    Key function for `group_auctions`.

    Accesses the comment/product name, and mangles it.
    If there is a '|' character present in the comment, only text to the
    left of the '|' is returned. All other text is ignored.
    '''
    comment_raw = auction.comment
    prod_name = comment_raw.split('|')[0].strip()
    return prod_name

def group_auctions(auction_list, key):
    '''
    Group auctions into lists with the same key.

    The key is accessed, and possibly brought to a normalized form,
    by the function `key`.

    Intended to group auctions according to category/tab or comment.

    ARGUMENT
    --------

    auction_list : list[auction]
        list of Auction instances

    key : function( Auction ): str
        Function to access (and possibly mangle) the grouping key.
        Takes an Auction as its argument and returns a string.

    RETURN
    ------

    dict[str -> list[auction]]
        Dictionary that maps key strings, to lists of auctions that belong
        to the same key (category/tab/comment).
    '''
    auct_dict = {}

    for auction in auction_list:
        key_str = key(auction)
        if key_str in auct_dict:
            auct_dict[key_str].append(auction)
        else:
            auct_dict[key_str] = [auction]

    return auct_dict



def filter_names(include_patterns, exclude_patterns, name_list):
    '''
    Remove names from a list, depending on patterns for inclusion and exclusion.

    Uses shell globbing for the patterns. For example "Nikon *" matches
    "Nikon Cameras" and "Nikon Lenses".
    '''
    filtered_names = set()
    #include names that match the inclusion patterns
    for pattern in include_patterns:
        match_names = [name for name in name_list if fnmatch.fnmatch(name, pattern)]
        filtered_names.update(set(match_names))
    #exclude the names that match the exclusion patterns
    for pattern in exclude_patterns:
        match_names = [name for name in filtered_names if fnmatch.fnmatch(name, pattern)]
        filtered_names.difference_update(set(match_names))

    return list(filtered_names)



def filter_group_auctions(auction_list, patterns_in, patterns_ex, key):
    '''
    Selects auctions according to the user's criteria,
    and groups them into lists, with the same key value.
    '''
    # create dictionary {category/comment : list of auctions}
    groups_raw = group_auctions(auction_list, key=key)
    # select the desired key strings
    good_keys = filter_names(patterns_in, patterns_ex, groups_raw.keys())
    # select the auction lists with the desired keys
    groups_filt = {}
    for name in good_keys:
        groups_filt[name] = groups_raw[name]

    return groups_filt



def filter_toplevel(auction_list, task):
    '''
    Include and exclude auctions according to patterns in task.
    Group auctions according to task.
    '''
    #select the desired categories, group auctions with same category
    cats_dict = filter_group_auctions(auction_list, task.cats_in, task.cats_ex,
                                      key=get_category)

    if len(cats_dict) == 0:
        raise UserError('No tab selected. See options "-t" and "-T"')

    #User wants no grouping of auctions with respect to categories/tabs
    #All auctions get into single list
    if not task.group_cats:
        cats_dict = {'': chain(*cats_dict.values())}

    #If there is only one category/tab its name should not appear in the legend
    if len(cats_dict) == 1:
        cats_dict = {'': cats_dict.values()[0]}

    #inside each category select and group according to comments
    out_dict = {}
    for cat, cat_aucts in cats_dict.iteritems():
        #select desired comments, group according to comments if desired
        comms_dict = filter_group_auctions(cat_aucts,
                                           task.comms_in, task.comms_ex,
                                           key=get_prod_comment)
        if not task.group_comms:
            comms_dict = {'': list(chain(*comms_dict.values()))}

        #create new dictionary with keys: category + comment
        for comm, auction_list2 in comms_dict.iteritems():
            out_key = (cat + ' ' + comm).strip()
            out_dict[out_key] = auction_list2

    return out_dict



def select_dates_prices(auction_list, price_name):
    '''
    Select the dates and price information from a list of auctions.
    Only auctions that were sold are considered.
    
    ARGUMENTS
    ---------
    auction_list: list[Auction]
        List of auctions, the dates and prices are taken from the auctions 
        in this list.
    price_name: str
        Name of the price column/field, that is selected. The names are 
        converted to lower case. Supported columns are:
        "Total", "Shipping", "Current"

    RETURNS
    ------
    list[float], list[float]
    dates, prices
    '''
    name_normalized = price_name.strip().lower()
    if name_normalized == 'total':
        getter = attrgetter('total_price')
    elif name_normalized == 'shipping':
        getter = attrgetter('shipping_price')
    elif name_normalized == 'current':
        getter = attrgetter('item_price')
    else:
        raise UserError('Unknown column {0}.'.format(price_name))

    dates, prices = [], []
    for auction in auction_list:
        if not auction.complete:
            continue
        if auction.bid_count <= 0:
            continue
        
        price = getter(auction)
        #remove nan, inf
        if not isfinite(price):
            continue

        prices.append(price)
        dates.append(auction.end_time)

    return dates, prices



def td_total_seconds(td):
    '''
    Convert a timedelta object to seconds.
    
    This function is part of a workaround for a bug in 
    matplotlib.pyplot.plot_date:
    Bug #3176823 "plot_date does not respect timezone"
    http://sourceforge.net/tracker/?func=detail&aid=3176823&group_id=80706&atid=560720
    '''
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6



def days_utc2local(utc_days):
    '''
    Convert an array of days in utc to local time. 
    Adds a fraction of a day.
    
    This function is part of a workaround for a bug in 
    matplotlib.pyplot.plot_date:
    Bug #3176823 "plot_date does not respect timezone"
    http://sourceforge.net/tracker/?func=detail&aid=3176823&group_id=80706&atid=560720
    '''
    seconds_day = 24 * 60 * 60
    timezone = dateutil.tz.tzlocal()
    dates = matplotlib.dates.num2date(utc_days)
    utc_offsets = zeros_like(utc_days)
    for i in range(len(utc_days)):
        offset_td = timezone.utcoffset(dates[i])
        utc_offsets[i] = td_total_seconds(offset_td)/seconds_day
        
    return utc_days + utc_offsets



def plot_line(date_list, price_list, label_str,
               color='blue', style='-', marker='o', avg_length=31):
    '''
    Plot one line into the current graph.
    '''
    assert len(date_list) == len(price_list)

    #special case: label_str is empty string, Matplotlib would hide this label
    label_str = '" "' if label_str == '' else label_str

    #Line with no points.
    #For example: All auctions with this label are unfinished.
    if len(date_list) == 0:
        print >> sys.stderr, 'Warning: Empty line! label: ' + label_str
        return

    #sort with dates as key. Array must be transposed for it.
    dp_u = array([date_list, price_list], 'd')
    s_temp = sorted(dp_u.T, key=lambda x: x[0])
    dp_s = array(s_temp).T
    dates = dp_s[0]
    prices = dp_s[1]

    #Convert to local time (adds fraction of day)
    #Workaround for Bug #3176823 "plot_date does not respect timezone"
    dates = days_utc2local(dates)
    
    #Compute moving average.
    avg_length = abs(avg_length)
    if dates[-1] - dates[0] < avg_length:
        #The averaged data is very short, compute mean and put it on short line
        avg_prices = ones((2,)) * median(prices)
        avg_dates = ones((2,)) * dates[0] + array([0, avg_length])
    else:
        #compute moving average over `avg_length` days
        avg_prices = zeros_like(prices)
        avg_dates = dates
        for i in range(len(dates)):
            curr_day = dates[i]
            avg_start = curr_day - avg_length / 2
            avg_stop  = curr_day + avg_length / 2
            avg_window = (avg_start <= dates) & (dates <= avg_stop)

            avg_prices[i] = median(prices[avg_window])

    #Workaround for Bug #3176823 "plot_date does not respect timezone"
    #timezone = dateutil.tz.tzlocal()
    timezone = matplotlib.dates.UTC
    #Plot moving average. Use pyplot.errorbar instead?
    plot_date(avg_dates, avg_prices, linestyle=style, marker=marker,  color=color,
              linewidth=2, markersize=5, markevery=(0, 100000), tz=timezone, 
              label=label_str)
    #plot prices
    plot_date(dates, prices, linestyle=' ', marker=marker, color=color,
              linewidth=2, markersize=5, tz=timezone, label=None)
    return



def get_color_style_marker(n):
    '''
    Return a tuple (color, line_style, marker) from a circular list of unique
    tuples. All items are format strings for Matplotlib.

    line_style and marker change in lock step.
    '''
    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']
    line_styles = ['-', '--', '-.', ':']
    markers =['o', 's', '^', 'v', ]

    color = colors[n % len(colors)]
    line_style = line_styles[(n // len(colors)) % len(line_styles)]
    marker =         markers[(n // len(colors)) % len(line_styles)]
    return color, line_style, marker



def make_chart_title(task):
    '''
    Create a chart's title, depending on the data in the task.
    '''
    if task.chart_title:
        #User set a chart title
        chart_title = task.chart_title
    elif task.input_file:
        #Reading from user selected file. Use filename and column as title.
        base_name = os.path.basename(task.input_file)
        root_name, _ = os.path.splitext(base_name)
        chart_title = root_name + ' - ' + task.column_name
    elif len(task.cats_in) == 1:
        #One tab selected. Use name of tab and column as title.
        chart_title = task.cats_in[0] + ' - ' + task.column_name
    else:
        chart_title = task.column_name
    return chart_title



def action_graph(auction_list, task):
    '''
    Create a graph.
    '''
    #Select auctions and group them, as desired by the user
    auct_dict = filter_toplevel(auction_list, task)

    #sort sequences according to product names
    line_names = sorted(auct_dict.keys())

    #Create plot window
    fig = figure()
    title(make_chart_title(task))
    #plot: each group of auctions is drawn as one smoothed line: price vs. time
    for n, name in enumerate(line_names):
        auction_list = auct_dict[name]
        date, price = select_dates_prices(auction_list, task.column_name)
        color, style, marker = get_color_style_marker(n)
        plot_line(date, price, name, color, style, marker, task.avg_length)
    #Create legend in current graph
    legend()

    #save figure as an image file if requested
    if task.output_img:
        fig.savefig(task.output_img)
    #show interactive window if desired
    if task.show_window:
        show()

    return



def action_list(auction_list, task):
    '''
    List the available categories/tabs
    '''
    #User has not supplied pattern for tabs to list: list all
    cats_in = task.cats_in if task.cats_in != [''] else ['*']

    cat_dict = filter_group_auctions(auction_list, cats_in, task.cats_ex,
                                     key=get_category)
    cats_sorted = sorted(cat_dict.keys())

    print 'Tab             : Auctions'
    print '--------------------------'
    auct_total = 0
    for cat in cats_sorted:
        n_auct = len(cat_dict[cat])
        auct_total += n_auct
        print '{c:15} : {n} '.format(c=cat, n=n_auct)

        #More information is requested
        #TODO: ls -l output is completely useless. Too ugly!
        if task.long_output >=1:
            for auction in cat_dict[cat]:
                print auction
    print
    print '{a} auctions in {t} tabs.'.format(a=auct_total, t=len(cat_dict))



def interpret_command_line():
    '''Parse the command line, and find out what the user wants from us.'''
    #set up parser for the command line aruments
    optPars = optparse.OptionParser(
                    usage='%prog [<command>] -t <tab name> [<options>]',
                    description=
'''Analysis program for prices on Ebay, for use in conjunction with JBidwatcher.
Prints price vs. time diagrams, with moving median price.
The program understands two commands: "graph" and "ls". If no command is given,
"graph" is assumed.
''',
                    #epilog = 'More help.',
                    version='%prog ' + PROGRAM_VERSION)

    optPars.add_option('-t', '--include-tabs', dest='cats_in', default='',
                       help='Tabs that should be analyzed. '
                       'Shell-style wildcards can be used. '
                       'For example "Nikon*" matches all names that start with '
                       '"Nikon". '
                       'Default: ""; MUST BE SUPPLIED FOR GRAPHS',
                       metavar='<tab name,...>')
    optPars.add_option('-T', '--exclude-tabs', dest='cats_ex',
                       help='Tabs that should NOT be analyzed. '
                       'Shell-style wildcards can be used. '
                       'Default: No default',
                       metavar='<tab name,...>')
    optPars.add_option('-c', '--include-comments', dest='comms_in', default='*',
                       help='Comments that should be analyzed. '
                       'Shell-style wildcards can be used. '
                       'Default: "*" (All comments)',
                       metavar='<comment name,...>')
    optPars.add_option('-C', '--exclude-comments', dest='comms_ex',
                       help='Comments that should NOT be analyzed. '
                       'Shell-style wildcards can be used. '
                       'Default: No default',
                       metavar='<comment name,...>')
    optPars.add_option('-u', '--analyze-column', dest='column_name',
                       default='Total',
                       help='column that should be analyzed. Default: Total',
                       metavar='<column>')
    optPars.add_option('-g', '--group-auctions', dest='group_auctions',
                       choices=['tc', 't', 'c', '_'], default='tc',
                       help='group auctions into lines. '
                       '"t": auctions from different tabs get into different lines; '
                       '"c": use comments; '
                       '"tc": both criteria; '
                       '"_": all selected auctions get in one line. '
                            'Default: "tc"',
                       metavar='<format string>')
    optPars.add_option('-i', '--input-file', dest='input_file',
                       help='name of input file that contains price '
                            'information. Default: '
                            '"~/.jbidwatcher/auctions.xml"',
                       metavar='<file name>')
    optPars.add_option('-o', '--output-image', dest='output_img',
                       help='store generated graph as (PNG) image in the '
                            'current directory. Default: do not store image.',
                       metavar='<file name>')
    optPars.add_option('-b', '--batch', dest='batch',
                       action="store_true", default=False,
                       help='batch operation. Do not show any graph windows. '
                            'Default: False')
    optPars.add_option('-l', '--long-output', dest='long_output',
                       action="count", default=False,
                       help='show more information. Default: False')
    optPars.add_option('--title', dest='chart_title',
                       help='Title of the chart. '
                            'Default: Program creates title',
                       metavar='<title string>')
    optPars.add_option('-w', '--window', dest='window_length',
                       type='float', default=31,
                       help='length of the window for computing the moving '
                            'median. Default: 31',
                       metavar='<number of days>')

    #do the parsing
    (options, args) = optPars.parse_args()

    #get command
    if len(args) > 0:
        command = args[0]
    else:
        command = 'graph'

    #Get the names of tabs, that should be analyzed
    cats_in = options.cats_in.split(',')
    #Get the names of tabs, that should be excluded
    cats_ex = options.cats_ex.split(',') \
              if options.cats_ex is not None else []
    #Get the names of comments, that should be analyzed
    comms_in = options.comms_in.split(',')
    #Get the names of comments, that should be excluded
    comms_ex = options.comms_ex.split(',') \
               if options.comms_ex is not None else []
    #Get the names of columns, that should be analyzed
    column_name = options.column_name

    #Options for grouping.
    if options.group_auctions == 'tc':
        group_cats, group_comms = True, True
    elif options.group_auctions == 't':
        group_cats, group_comms = True, False
    elif options.group_auctions == 'c':
        group_cats, group_comms = False, True
    else:
        group_cats, group_comms = False, False

    #Get name of input file or None
    input_file = options.input_file
    #Get name of output image or None
    output_img = options.output_img
    #should interactive graphs be shown?
    show_window = not options.batch
    #should more information be shown?
    long_output = options.long_output
    #Get user supplied chart title
    chart_title = options.chart_title

    #get length of moving mean filter
    avg_length = abs(options.window_length)

    #Store all the options in a Task object
    task = Task(action=command,
                input_file=input_file, output_img=output_img,
                show_window=show_window,
                cats_in=cats_in, cats_ex=cats_ex, group_cats=group_cats,
                comms_in=comms_in, comms_ex=comms_ex, group_comms=group_comms,
                column_name=column_name, avg_length=avg_length,
                chart_title=chart_title, long_output=long_output)
    #print pprint.pformat(task)
    return task



def main():
    '''
    Main function and staring point of Ebay price statistics program.
    '''
    task = interpret_command_line()

    try:
        if task.input_file:
            file_name = task.input_file
        else:
            file_name = find_xml_file()
        file_text = open(file_name, 'r').read()

        #print modification time and age of input file
        mod_stamp = os.path.getmtime(file_name)
        mod_time = datetime.datetime.utcfromtimestamp(mod_stamp)
        now = datetime.datetime.utcnow()
        data_age = now - mod_time
        print "Data from: {t} UTC. Age: {a} hours.".format(a=data_age, 
                                                           t=mod_time)

        _, extension = os.path.splitext(file_name)
        if extension.lower() == '.xml':
            auction_list = interpret_xml(file_text)
        elif extension.lower() == '.csv':
            auction_list = interpret_csv(file_text)
        else:
            raise UserError('Unknown extension {0}'.format(extension))

        if task.action == 'ls':
            action_list(auction_list, task)
        elif task.action in ('graph', 'gr'):
            action_graph(auction_list, task)
        else:
            raise UserError('Unknown command {0}.'.format(task.action))

    except UserError, err:
        print >> sys.stderr, 'Error:', err
        exit(1)
    except IOError, err:
        print >> sys.stderr, 'Error:', err
        exit(1)



if __name__ == '__main__':
    # File is run as script. Start main function.
    # The tests functions import this file as a module, then this code won't
    # be executed.
    main()
