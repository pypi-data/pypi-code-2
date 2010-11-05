'''
Created on 4 nov. 2010

@author: Arnaud
'''
from pyxontime import get_bus_stop_schedules
from pyxontime import persist

def exec_store_menu():
    """Show stored bus stops
    
    """
    loop = False
    
    bus_stops = persist.read()
    if bus_stops:
        loop = True
        print "Here are the bus stop you've stored so far:"
        for name, code, link in bus_stops:
            print name.ljust(20) + " -> " + code
    
    while loop:
        stop_code = raw_input("\nGimme its code (or go 'back'):\n>")
        if stop_code == "back":
            break
        else:
            for name, code, link in bus_stops:
                if stop_code == code:
                    schedules = get_bus_stop_schedules(link)
                    if schedules:
                        print "\nService -> Destination -> Departure\n==================================="
                        for service, destination, departure, null in schedules:
                            print "%s -> %s -> %s" % (service.ljust(10), destination.ljust(25), departure)
                            loop = False
                            break