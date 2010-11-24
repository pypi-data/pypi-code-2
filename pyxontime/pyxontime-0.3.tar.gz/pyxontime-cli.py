'''
Created on 2 nov. 2010

@author: Arnaud
'''
from pyxontime.cli import search, store
import urllib2

def print_menu():
    print """Hello ! Welcome to PyxfordBus, your Python friend to\nfind OxfordBus Company times or departure/arrive !\nMenu :
    1- Search for a bus stop
    2- View schedules for a stop I saved"""

if __name__ == "__main__":
    print_menu()
    choice = raw_input("Press 1 or 2: (or 'quit')\n>")
    
    while True:
        if choice == "quit":
            break
        if choice == "1":
            search.exec_search_menu()
        if choice == "2":
            store.exec_store_menu()
        
        print_menu()
        choice = raw_input("Press 1 or 2: (or 'quit')\n>")
