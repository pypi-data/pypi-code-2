#define a function
def print_lol (the_list, level=0):
    for a_element in the_list:#foreach
        if(isinstance(a_element,list)):#check type
            print_lol(a_element, level+1)#iteration
        else:
            for tab_stop in range(level):#print the tab as many as the level
                print "\t",
            print a_element
