#!/usr/bin/env python
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
import time
import datetime
import fnmatch
import optparse
import subprocess
import ConfigParser
import xml.etree.ElementTree as et
from types import NoneType
from collections import namedtuple, defaultdict
from itertools import chain
from operator import attrgetter
from numpy import nan, array, ones, zeros_like, median, isfinite
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import dateutil
#import pprint



PROGRAM_VERSION = '0.1.7'
PROGRAM_NAME = 'ebstat.py'



class UserError(Exception):
    '''
    Exception for regular fatal program error, that was cause by faulty user
    input. As opposed to a program internal error.
    '''



BaseAuction = namedtuple('Auction', 'id, end_time, '
                                    'item_price, shipping_price, currency,'
                                    'comment, category,'
                                    'complete, bid_count')
class Auction(BaseAuction): #IGNORE:W0232
    '''
    Represents one Ebay auction.

    Inherits from a named tuple for the generated __repr__ and __init__
    functions.
    '''
    @property
    def total_price(self):
        '''Compute total price on the fly'''
        return self.item_price + self.shipping_price #IGNORE:E1101



#Object that encodes the user's command. Attributes mostly correspond to 
#command line options.
Task = namedtuple('Task', 'action, input_file, output_img, show_window, '
                          'cats_in, cats_ex, group_cats, '
                          'comms_in, comms_ex, group_comms, '
                          'column_name, window_length, chart_title, '
                          'long_output, legend_position, '
                          'double_click_command')

def make_task(*args, **kwargs):
    '''
    Create a Task object without the need to specify all attributes.
    Useful for tests. In most tests only few of the Task's attributes are used.
    '''
    #pylint: disable-msg=W0212,W0142
    #Create dict with all legal keyword arguments as keys, values are None 
    all_kwargs = dict([(f, None) for f in Task._fields])
    
    #Put the positional arguments into the dict
    for name, val in zip(Task._fields, args):
        all_kwargs[name] = val
    #Put the keyword arguments into the dict
    for name, val in kwargs.iteritems():
        if name not in all_kwargs:
            raise TypeError('Undefined field name: ' + str(name))
        all_kwargs[name] = val
        
    return Task(**all_kwargs)

    

class EventReceiver(object):
    """
    Receive various events and trigger the appropriate actions.
    The events are interrelated. 
    
    * The class creates (most of) the text in the tool-bar during mouse 
      movements, which shows time and price at the cursor position.
    * When an auction (symbol) is clicked, the auction's ID, time, and price
      are shown in the tool bar. This greatly reduces the need for zooming.
    * When an auction is double-clicked, a configurable external program is 
      run. 
    """
    def __init__(self, figure, double_click_command):
        #represents whole interactive graph
        self.figure = figure
        #Formats dates on X-Axis
        self.date_formatter = mdates.DateFormatter('%Y-%m-%d %H:%M (%a)')
        #store the auctions' IDs, for each line. dict[Line >> list[int]]
        #relates: picked line >> list of IDs 
        self.auction_ids = {}
        #Time when a mouse button was pressed, used for detecting double clicks
        self.old_button_press_time = 0.
        self.double_click_interval = 0.5
        self.picked_auction_id = None
        #Command that is executed when the user double-clicks
        #Run Firefox: http://cgi.ebay.de/ws/eBayISAPI.dll?ViewItem&item={ID}
        self.double_click_command = double_click_command
        
        #Connect some of the callback functions to events
        #`create_date_text` and `create_price_text` are connected separately
        self.figure.canvas.mpl_connect('pick_event', self.on_pick_event)
        self.figure.canvas.mpl_connect('button_press_event', 
                                       self.on_button_press_event)
        self.figure.canvas.mpl_connect('motion_notify_event', 
                                       self.on_motion_notify_event)


    def add_pick_info(self, line, ids):
        '''
        Add a line and an array of auction IDs to the picking information.
        Needed for picking auctions.
        '''
        self.auction_ids[line] = ids
        
        
    def create_date_text(self, date):
        '''
        Create text that appears in the toolbar that shows the cursor position
        on the time axis
        Called when mouse moves.
        '''
        return self.date_formatter(date)
    
    
    def create_price_text(self, price):
        '''
        Create text that appears in the toolbar that shows the cursor position
        on the price axis
        Called when mouse moves.
        '''
        return '{0:.2f}'.format(price)
    
    
    def on_pick_event(self, event):
        '''
        Put information about picked auction into tool bar, and store ID of 
        picked auction.
        Called when the user presses a mouse button over an object.
        '''
        #get the interesting data from the event
        pick_line = event.artist
        xdata = pick_line.get_xdata()
        ydata = pick_line.get_ydata()
        ind0 = event.ind[0] #multiple points can be picked at once
        
        #Create tool-bar message with data from picked auction
        auction_id = self.auction_ids[pick_line][ind0]
        date, price = xdata[ind0], ydata[ind0]
        msg = 'ID: {i} x={t} y={p}'.format(i=auction_id,
                                           t=self.create_date_text(date), 
                                           p=self.create_price_text(price))
        self.figure.canvas.toolbar.set_message(msg)
        
        #Remember ID of picked auction for the double click.
        self.picked_auction_id = auction_id
        
        
    def on_button_press_event(self, _event):
        '''
        Detect double click, and perform the configured action.
        Called when the mouse button is pressed
        '''
        #do time keeping
        curr_time, old_time = time.time(), self.old_button_press_time
        self.old_button_press_time = curr_time
        
        #A double click was detected.
        if curr_time - old_time < self.double_click_interval:
            print 'double clicked auction:', self.picked_auction_id
            #Run configurable program
            if self.picked_auction_id:
                args = self.double_click_command \
                           .replace('{ID}', str(self.picked_auction_id))
                print 'Running:', args
                subprocess.Popen(args, close_fds=True, shell=True,)


    def on_motion_notify_event(self, _event):
        '''
        Delete the stored ID of the picked auction. The cursor has moved, the 
        auction is no longer picked.
        Called when the mouse is moved.
        '''
        self.picked_auction_id = None


#    def on_release_event(self, event):
#        '''
#        Called when the mouse button is released
#        '''
#        pass



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
    epoch2num = mdates.epoch2num
    auction_list = []
    root_xml = et.fromstring(xml_text)
    server_xml = root_xml.find('auctions/server/')
    for auct_xml in server_xml:
        info_xml = auct_xml.find('info')
        auction_id = long(auct_xml.get('id'))
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
        auct_id = long(line_dict['Number'])
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
        num = mdates.date2num(date)
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

    defaultdict[str -> list[auction]]
        Dictionary that maps key strings, to lists of auctions that belong
        to the same key (category/tab/comment).
    '''
    #when a key is not in the dict it is inserted like so: ``key: list()`` 
    auct_dict = defaultdict(list)

    for auction in auction_list:
        key_str = key(auction)
        auct_dict[key_str].append(auction)

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



def select_plot_columns(auction_list, price_name):
    '''
    Create price, date, and auctions ID lists from a list of auctions.
    Only auctions that were sold are considered.

    Matplotlib's plot function wants lists of X- and Y-values for plotting.
    The auctions IDs are used to identify the auctions when they are clicked 
    (picked) in the interactive graph.

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
    list[float], list[float], list[long]
        dates, prices, auction IDs
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

    dates, prices, ids = [], [], []
    for auction in auction_list:
        #Test if item was sold
        if not auction.complete:
            continue
        if auction.bid_count <= 0:
            continue
        
        #get the desired price, but we want no nan, inf
        price = getter(auction)
        if not isfinite(price):
            continue
        
        #Append the data to their respective lists
        prices.append(price)
        dates.append(auction.end_time)
        ids.append(auction.id)
        
    return dates, prices, ids



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
    dates = mdates.num2date(utc_days)
    utc_offsets = zeros_like(utc_days)
    for i in range(len(utc_days)):
        offset_td = timezone.utcoffset(dates[i])
        utc_offsets[i] = td_total_seconds(offset_td)/seconds_day
        
    return utc_days + utc_offsets



def plot_line(date_list, price_list, label_str,
               color='blue', style='-', marker='o', window_length=31):
    '''
    Plot one line into the current graph.
    
    Returns
    -------
    
    Line2D
        Line that shows the auction prices.
    
    The return value is used for picking (clicking) auctions in the 
    interactive window.
    '''
    assert len(date_list) == len(price_list)

    #special case: label_str is empty string, Matplotlib would hide this label
    label_str = '" "' if label_str == '' else label_str

    #Line with no points.
    #For example: All auctions with this label are unfinished.
    if len(date_list) == 0:
        print >> sys.stderr, 'Warning: Empty line! label: ' + label_str
        return

    dates = array(date_list, 'd')
    prices = array(price_list, 'd')

    #Convert to local time (adds fraction of day)
    #Workaround for Bug #3176823 "plot_date does not respect timezone"
    dates = days_utc2local(dates)
    
    #Compute moving average.
    window_length = abs(window_length)
    if dates[-1] - dates[0] < window_length:
        #The averaged data is very short, compute mean and put it on short line
        avg_prices = ones((2,)) * median(prices)
        avg_dates = ones((2,)) * dates[0] + array([0, window_length])
    else:
        #compute moving average over `window_length` days
        avg_prices = zeros_like(prices)
        avg_dates = dates
        for i in range(len(dates)):
            curr_day = dates[i]
            avg_start = curr_day - window_length / 2
            avg_stop  = curr_day + window_length / 2
            avg_window = (avg_start <= dates) & (dates <= avg_stop)

            avg_prices[i] = median(prices[avg_window])

    #Workaround for Bug #3176823 "plot_date does not respect timezone"
    #timezone = dateutil.tz.tzlocal()
    timezone = mdates.UTC
    #Plot moving average. Use pyplot.errorbar instead?
    plt.plot_date(avg_dates, avg_prices, 
                  linestyle=style, marker=marker, color=color,
                  linewidth=2, markersize=5, markevery=(0, 100000),
                  tz=timezone, label=label_str)
    #plot real prices
    line, = plt.plot_date(dates, prices, 
                          linestyle=' ', marker=marker, color=color, 
                          linewidth=0, markersize=5, 
                          tz=timezone, label=None, picker=4)

    return line



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
        #Only one tab pattern given. Use this pattern and column as title.
        chart_title = task.cats_in[0] + ' - ' + task.column_name
    else:
        chart_title = task.column_name
        
    #add length of window information
    chart_title += '   (median: {d:g} days)'.format(d=task.window_length)
    return chart_title



def action_graph(auction_list, task):
    '''
    Create a graph.
    
    Arguments
    ---------
    
    auction_list : list[Action]
        List of (all) auctions, that were read from the input file.
        
    task : Task
        Record containing the program options.
    '''
    #Select auctions and group them, as desired by the user
    auct_dict = filter_toplevel(auction_list, task)

    #sort sequences according to product names
    line_names = sorted(auct_dict.keys())

    #Create plot window and object to handle interactive events
    fig = plt.figure()  
    ev_rec = EventReceiver(fig, task.double_click_command)
    
    #plot: auctions of each product are drawn independently
    for n, name in enumerate(line_names):
        #get list of auctions and sort it according to the auctions' end dates
        auction_list = sorted(auct_dict[name], key=lambda auct: auct.end_time)
        #create lists of numerical data; select a price column 
        dates, prices, id_list = select_plot_columns(auction_list, 
                                                     task.column_name)
        #create unique plot style, and create plot for one product
        color, style, marker = get_color_style_marker(n)
        line = plot_line(dates, prices, 
                         name, color, style, marker, task.window_length)
        #Give line and auction Ids to event handler for picking
        ev_rec.add_pick_info(line, id_list)
        
    #Set chart title
    plt.title(make_chart_title(task))
    #Create legend and make it half transparent, default: loc='best'
    leg = plt.legend(loc=task.legend_position)
    if leg: 
        leg.get_frame().set_alpha(0.5)
    #rotate date labels, so that they don't overlap
    fig.autofmt_xdate()
    #set the functions, that create the text in the graph's lower right corner
    axes = plt.gca()
    axes.fmt_xdata = ev_rec.create_date_text
    axes.fmt_ydata = ev_rec.create_price_text
    
    #save figure as an image file if requested
    if task.output_img:
        fig.savefig(task.output_img)   
    #show interactive window if desired, run the GUI's event loop.
    if task.show_window:
        plt.show() 

    return 
   
   

def action_list(auction_list, task):
    '''
    List the available categories/tabs
    '''
    #If user has not supplied pattern for tabs to list: list all tabs
    cats_in = task.cats_in if task.cats_in != [] else ['*']
    #The list action wants to group the auctions always according to the tabs
    task_new = task._replace(group_cats=True, group_comms=False, # pylint: disable-msg=W0212
                             cats_in=cats_in)
    
    #Select the auctions that the user wants to list, and group them according 
    #to the tabs/categories.
    cat_dict = filter_toplevel(auction_list, task_new)
    
    #Work around special behavior of filter_toplevel(...)
    #If only one category is selected its name is erased.
    if cat_dict.keys() == ['']:
        aucts = cat_dict['']
        category = aucts[0].category
        cat_dict = {category: aucts}
    
    cats_sorted = sorted(cat_dict.keys())

    print 'Tab             : Auctions'
    print '--------------------------'
    auct_total = 0
    for cat in cats_sorted:
        n_auct = len(cat_dict[cat])
        auct_total += n_auct
        print '{c:15} : {n} '.format(c=cat, n=n_auct)

        #More information is requested
        #TODO: ls -l output is extremely ugly!
        if task.long_output >=1:
            for auction in cat_dict[cat]:
                print auction
            print "\n"
    print
    print '{a} auctions in {t} tabs.'.format(a=auct_total, t=len(cat_dict))



class OptionRCParser(object):
    '''
    Parser for command line options, that additionally uses a RC file.
    
    Has similar interface like `optparse.OptionParser`.
    '''
    def __init__(self, program_name='**Name**', version='**Version**', 
                  rc_dir='~', usage=None, description=None, epilog=None):
        #Create parser for command line options
        self.option_parser = optparse.OptionParser(
                                        usage=usage, description=description, 
                                        epilog=epilog, version=version, 
                                        prog=program_name)
        
        #create parser for RC file (and also store its name)
        rc_dir = os.path.expanduser(rc_dir)
        self.rc_file_name = os.path.join(rc_dir, '.' + program_name + '-rc')
        self.config_parser = ConfigParser.SafeConfigParser()
        self.config_parser.read(self.rc_file_name)
        
        #Program name and version string, for header comment in RC file
        self.program_name = program_name
        self.version = version
        #dict[option name >> Option instance]
        self.options = {}
        #parse result: dict[option name >> option value] 
        self.parsed_opt_vals = {}
        #parse result: list[program arguments]
        self.parsed_arg_vals = []
        #str : Name of active section in config file.
        self.active_section = 'default-section'
    
    
    def add_option(self, short_opt, long_opt, **attrs):
        '''
        Add an option to the parser.
        
        Accepts the same arguments as `optparse.OptionParser.add_option`.
        However `dest="..."` is ignored. `default="..."` should also
        not be used. 
        
        ARGUMENTS
        ---------
        
        short_opt : str, NoneType
            The short option string. For example "-a". May be None.
            
        long_opt : str
            The long option string. For example "--add-frob". 
            
            long_opt with the leading minus characters removed is the option's 
            name. In the example above the name would be "add-frob".
            
        The following arguments are optional keyword arguments.
        
        help : str
            The help string for this option.
        
        metavar : str
            String that symbolizes the option's argument in the generated 
            help text.
            
        type : str = "str"
            Type of the option's value. This results in type checking the 
            value and a special error message when the type check fails.
            Note: All values are returned as strings however!
            
            Known values are: str, int, float, choices
        
        choices : list[str]
            List of possible option values. Implies type="choices".
        
        action : str
            Action that the parser should perform when it recognizes an 
            option.
            
            Known values are: store, store_true, store_false, store_const, 
                              count, append, callback
        '''
        assert isinstance(long_opt, str)
        #TODO: better test. long opt may only contain a-z,A-Z,0-9
        assert '_' not in long_opt, 'Option names must not contain underlines.'
        assert len(long_opt) >= 3, 'long_opt must conform to pattern "--name"'
        option_name = long_opt[2:] #remove the '--' from the long option
        #Set the result name for option parser. 
        #It is equal to the long option name but '-' is replaced by '_'
        attrs['dest'] = option_name.replace('-', '_')
        option = optparse.Option(short_opt, long_opt, **attrs)
        #Add option to parser and to our own list
        self.option_parser.add_option(option)
        self.options[option_name] = option
        
        
    def parse_args(self, args=None):
        '''
        Parse the command line arguments. 
        
        ARGUMENT
        --------
        args : list[str]
            Can be used instead of the command line arguments for testing.
            If None, sys.argv[1:] is used.
        '''
        opt_vals, self.parsed_arg_vals = self.option_parser.parse_args(args)
        #Put parsed option values into a dict, the key is the option's 
        #original long name. 
        for name, val in opt_vals.__dict__.iteritems():
            name = name.replace('_', '-')
            if val is not None:
                self.parsed_opt_vals[name] = str(val)
    
    
    def get_arguments(self):
        '''
        Return the parsed command line arguments.
        
        RETURN
        ------
        list[str]
            The program's arguments in a list.
        '''
        return self.parsed_arg_vals
    
    
    def get_option(self, opt_name, default_val):
        '''
        Get the value of one option.
        
        The returned option value is taken from three potential sources:
        1. The parsed option values from the command line.
        2. The RC file. 
        3. The default value.
        
        ARGUMENT
        --------
        
        opt_name : str
            Name of the option. Same as long option without the "--"
            
        default_val : object
            The default value, whic is returned if option is neither in 
            command line nor in RC file.
            
        RETURN
        ------
        str
            The option's value.
        '''
        assert isinstance(opt_name, str)
        assert isinstance(default_val, (str, NoneType))
        if opt_name not in self.options:
            raise ValueError('Unknown option: ' + str(opt_name))
        if opt_name in self.parsed_opt_vals:
            return self.parsed_opt_vals[opt_name]
        elif self.config_parser.has_option(self.active_section, opt_name):
            return self.config_parser.get(self.active_section, opt_name)
        else:
            return default_val
    
    
    def get_bool(self, opt_name, default_val):
        '''
        Get a boolean option value. 
        Same as `get_option` but converts result to boolean.
        '''
        assert isinstance(default_val, bool)
        val = self.get_option(opt_name, str(default_val))
        if val == 'True':
            return True
        else:
            return False
        
    
    def set_rc_file_section(self, section_name):
        '''Set the section of the RC file that is accessed.'''
        self.active_section = section_name
    
    
    def write_options_to_rc_file(self):
        '''
        Store the current options in a RC file.
        The options that are specified on the command line, are stored in the 
        RC file in the current active section (set with 
        `self.set_rc_file_section(...)`).
        '''
        msg = \
'''#Configuration file for program "{p}" version {v}.
#This file contains default values for the command line options.

'''.format(p=self.program_name, v=self.version)                      
        #clear active section, create it if necessary
        if self.config_parser.has_section(self.active_section):
            self.config_parser.remove_section(self.active_section)
            self.config_parser.add_section(self.active_section)
        else:
            self.config_parser.add_section(self.active_section)
        #put the current options in the RC file/parser object
        for name, value in self.parsed_opt_vals.iteritems():
            self.config_parser.set(self.active_section, name, value)
        #write RC file to disk  
        print 'Writing configuration file: ' + self.rc_file_name
        fp = open(self.rc_file_name, 'w')
        fp.write(msg)
        self.config_parser.write(fp)
        fp.close()
    
    
    def remove_rc_file(self):
        '''Remove the rc file.'''
        print 'Removing configuration file: ' + self.rc_file_name
        try:
            os.remove(self.rc_file_name)
        except OSError:
            print 'No configuration file existed.'

        
    def error(self, msg):
        '''
        Print `msg` and `usage` message and exit program with error.
        '''
        self.option_parser.error(msg)



def split_None(string, sep):
    '''
    Split string into list of strings at sep. 
    If string is None an empty list is returned.
    '''
    if string is None:
        return []
    assert isinstance(string, str)
    return string.split(sep)



def interpret_command_line():
    '''Parse the command line, and find out what the user wants from us.'''
    #set up parser for the command line aruments
    parser = OptionRCParser(program_name=PROGRAM_NAME, 
                            version=PROGRAM_VERSION,
                            usage='%prog [<command>] -t <tab name> [<options>]',
                            description=
'''Analysis program for prices on Ebay, for use in conjunction with JBidwatcher.
Prints price vs. time diagrams, with moving median price.
The program understands four commands: "graph", "ls", "save-defaults", 
"clear-defaults". If no command is given, "graph" is assumed.
''',
                            #epilog = 'More help.',
                            )

    parser.add_option('-t', '--include-tabs', metavar='<tab name,...>',
                      help='Tabs that should be analyzed. '
                      'Shell-style wildcards can be used. '
                      'For example "Nikon*" matches all names that start with '
                      '"Nikon". '
                      'Default: "*"; (All tabs)',)
    parser.add_option('-T', '--exclude-tabs', metavar='<tab name,...>',
                      help='Tabs that should NOT be analyzed. '
                      'Shell-style wildcards can be used. '
                      'Default: Exclude no auction.',)
    parser.add_option('-c', '--include-comments', metavar='<comment name,...>',
                      help='Comments that should be analyzed. '
                      'Shell-style wildcards can be used. '
                      'Default: "*" (All comments)',)
    parser.add_option('-C', '--exclude-comments', metavar='<comment name,...>',
                      help='Comments that should NOT be analyzed. '
                      'Shell-style wildcards can be used. '
                      'Default: Exclude no auction.',)
    parser.add_option('-u', '--analyze-column', metavar='<column>',
                      help='Column that should be analyzed. Default: Total',)
    parser.add_option('-g', '--group-auctions', metavar='<format string>',
                      choices=['tc', 't', 'c', '_'], 
                      help='Group auctions into lines. '
                      '"t": auctions from different tabs get into different lines; '
                      '"c": use comments; '
                      '"tc": both criteria; '
                      '"_": all selected auctions get in one line. '
                           'Default: "tc"',)
    parser.add_option('-w', '--window', type='float', metavar='<number of days>',
                      help='Length of the window for computing the moving '
                           'median. Default: 31',)
    parser.add_option('-i', '--input-file', metavar='<file name>',
                      help='Name of input file that contains price '
                           'information. Default: '
                           '"~/.jbidwatcher/auctions.xml"',)
    parser.add_option('-o', '--output-image', metavar='<file name>',
                      help='Store generated graph as (PNG) image in the '
                           'current directory. Default: do not store image.',)
    parser.add_option('-b', '--batch', action="store_true", 
                      help='Batch operation. Do not show any graph windows. '
                           'Default: False')
    parser.add_option('-l', '--long-output', action="count", 
                      help='Show more information. Default: False')
    parser.add_option(None, '--title', metavar='<title string>',
                      help='Title of the chart. '
                           'Default: Program creates title',)
    parser.add_option(None, '--legend-position', metavar='<position>',
                      choices=['upper-left',  'upper-center', 'upper-right', 
                               'center-left', 'center',       'center-right', 
                               'lower-left',  'lower-center', 'lower-right',
                               'best'],
                      help='Position of the legend. Possible values are: '
                           'upper-left, upper-center, upper-right, '
                           'center-left, center, center-right, '
                           'lower-left, lower-center, lower-right, '
                           'best. '
                           'Default: best '
                           '(Best position is chosen automatically.)',)
    parser.add_option(None, '--double-click-command', metavar='<command>',
                      help='Command that is executed when the user performs '
                           'a double click. The string {ID} is replaced by '
                           "the auction's Ebay ID."
                           'Default: firefox "http://cgi.ebay.de/ws/eBayISAPI.dll?ViewItem&item={ID}" '
                           '(Start Firefox)',)

    #do the parsing
    parser.parse_args()

    #get command
    args = parser.get_arguments()
    if len(args) > 0:
        command = args[0]
    else:
        command = 'graph'
        
    #execute the commands "save-defaults", "clear-defaults"
    if command == 'save-defaults':
        parser.set_rc_file_section('graph')
        parser.write_options_to_rc_file()
        exit(0)
    elif command == 'clear-defaults':
        parser.remove_rc_file()
        exit(0)
    #let "graph" command read from its section of the configuration file,
    #to get the defaults for the options
    elif command in ('graph', 'gr'):
        parser.set_rc_file_section('graph')

    #Get the names of tabs, that should be analyzed
    cats_in = split_None(parser.get_option('include-tabs', '*'), ',')
    #Get the names of tabs, that should be excluded
    cats_ex = split_None(parser.get_option('exclude-tabs', None), ',')
    #Get the names of comments, that should be analyzed
    comms_in = split_None(parser.get_option('include-comments', '*'), ',')
    #Get the names of comments, that should be excluded
    comms_ex = split_None(parser.get_option('exclude-comments', None), ',')
    #Get the name of column, that should be analyzed
    column_name = parser.get_option('analyze-column', 'Total')

    #Options for grouping.
    ga = parser.get_option('group-auctions', 'tc')
    if ga == 'tc':
        group_cats, group_comms = True, True
    elif ga == 't':
        group_cats, group_comms = True, False
    elif ga == 'c':
        group_cats, group_comms = False, True
    else:
        group_cats, group_comms = False, False

    #get length of moving mean filter
    window_length = abs(float(parser.get_option('window', '31')))
    #Get name of input file or None
    input_file = parser.get_option('input-file', None)
    #Get name of output image or None
    output_img = parser.get_option('output-image', None)
    #should interactive graphs be shown?
    show_window = not parser.get_bool('batch', False)
    #should more information be shown?
    long_output = int(parser.get_option('long-output', '0'))
    #Get user supplied chart title
    chart_title = parser.get_option('title', None)
    #Position of figure's legend
    legend_position = parser.get_option('legend-position', 'best')
    legend_position = legend_position.replace('-', ' ')
    #Command that is executed when a double click is detected.
    cmd = 'firefox "http://cgi.ebay.de/ws/eBayISAPI.dll?ViewItem&item={ID}"'
    double_click_command=parser.get_option('double-click-command', cmd)

    #Store all the options in a Task object
    task = Task(action=command,
                input_file=input_file, output_img=output_img,
                show_window=show_window,
                cats_in=cats_in, cats_ex=cats_ex, group_cats=group_cats,
                comms_in=comms_in, comms_ex=comms_ex, group_comms=group_comms,
                column_name=column_name, window_length=window_length,
                chart_title=chart_title, long_output=long_output, 
                legend_position=legend_position, 
                double_click_command=double_click_command)
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
