""" some functions for list
    print_list(the_list)
    
    @author Tony Zhou
"""

def print_list (the_list):
    # print the list with nested list
    
    for item in the_list:
        if isinstance(item, list):
            print_list(item)
        else:
            print(item)
