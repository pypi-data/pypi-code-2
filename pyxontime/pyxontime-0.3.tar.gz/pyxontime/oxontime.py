'''
Created on 3 nov. 2010

@author: Arnaud
'''
from pyquery import PyQuery
import re
import sys
import unicodedata

host = 'http://www.oxontime.com'

def normalize_string (value):
    """Return an ascii normalized string without special characters,
       replacing all whitespaces by +
    """
    value = value.decode(sys.stdout.encoding)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = re.sub('[^\w\s]', '', value)
    value = re.sub('[\s]+', '+', value)
    return value

def get_bus_stop_code(name):
    """Return the code of a bus stop, giving its name
       [[Bus_stop_name, Bus_stop_code, Bus_stop_link]]
    """
    name = normalize_string(name)
    url = host + '/web/stop_reference.asp?areacode=&naptan=' + name + '&textonly=1'
    
    oxon = ""
    # Launch a PyQuery on the oxontime website for retrieving results about bus stops
    try:
        oxon = PyQuery(url=url)
    except:
        print "Error ! Please, first of all verify your internet connection."
    th_s = oxon('th')
    td_s = oxon('td')

    # The list which will be returned at the end
    li_s = []
    
    # If at least one <th> is found in the page, then we now that there is results to parse
    if th_s.eq(0).html() != None:
        # Get all the link (bus stop information) found
        a_s = td_s.find('a')
        
        # According to the site, we can get the number of the bus stop using this regexp
        pattern = re.compile(r'^\D+=([0-9]+)&\D+')

        # For each link <a> in the web page        
        for link in a_s:
            # Get its 'href' attribute (the link to get the schedules for that bus stop)
            href = link.get('href')
            # Get its code (using the regexp on the link)
            code = pattern.search(href).groups()[0]
            
            # After some tests, I realized that the bus stop code 0 can have several
            # different names, and correspond to several different location and never has bus schedules
            if code != "0":
                # Get the name of the bus stop
                text = link.text
                li_s.append([text, code])
    
    # Return the list of bus stops found according to the key word
    # [[Bus_stop_name, Bus_stop_code, Bus_stop_link], ..., [Bus_stop_name, Bus_stop_code, Bus_stop_link]]
    return li_s

def get_bus_stop_schedules(code):
    """Return the times of depart/arrive of coaches on a given bus stop code
       [[Service, Destination, Time_departure, Useless_string]]
    """
    url = host + "/pip/stop.asp?naptan=" + code + "&textonly=1"
    
    # Launch a PyQuery on the oxontime website for retrieving schedules about a bus stops
    try:
        d = PyQuery(url=url)
    except:
        print "Error ! Please, first of all verify your internet connection"
    th_s = d('th')
    td_s = d('td')
    
    # The list which will be returned at the end
    li_s = []
    # If at least one <th> is found in the page, then we now that there is schedules to parse
    if th_s.eq(0).html() != None:
        # Retrieve the schedules from the web page formated as follow:
        # [[Service, Destination, Time_departure, Useless_string]]
        li_s = [[item.text for item in td_s[i:i+4]] for i in range(0, len(td_s), 4)]
    
    # Return the list of schedules found for the given bus stop
    return li_s
