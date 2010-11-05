'''
Created on 4 nov. 2010

@author: Arnaud
'''
from pyxontime import get_bus_stop_code, get_bus_stop_schedules
from pyxontime import persist

def exec_search_menu():
    """Search for a bus stop and then the bus stop schedules
    """
    return_list = []
    while True:
        bus_search = raw_input("Enter a bus stop name to search for: (or quit)\n>")
        if bus_search == "quit":
            break
    
        bus_stops = get_bus_stop_code(bus_search)
    
        if bus_stops:
            print "\nStop Name -> Stop Code\n======================"
            for stop_name, stop_code, stop_link in bus_stops:
                print stop_name.ljust(20) + " -> " + stop_code
    
            while True:
                stop_code = raw_input("\nFound THE one ? Gimme its code ! :)\n>")
                if stop_code in [item[1] for item in bus_stops]:
                    break
    
            for name, code, link in bus_stops:
                if stop_code == code:
                    schedules = get_bus_stop_schedules(link)
                    if schedules:
                        print "\nService -> Destination -> Departure\n==================================="
                        for service, destination, departure, null in schedules:
                            print "%s -> %s -> %s" % (service.ljust(10), destination.ljust(25), departure)
                        while True:
                            resp = raw_input("\nSave this bus stop ? ('yes' or 'no')\n>")
                            if resp == "yes":
                                return_list = [code, name, link]
                                break
                            if resp == "no":
                                break
                    else:
                        print "\nNo schedules..."
    
        else:
            print "\nSorry buddy, no bus stop found..."
    
        break
    
    if return_list:
        persist.save(return_list[0], return_list[1], return_list[2])
