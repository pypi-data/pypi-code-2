""" some functions for list
    print_list(the_list)
    
    @author Tony Zhou
"""

def print_list (the_list, level):
    # print the list with nested list
    # insert some tab
    
    for item in the_list:
        if isinstance(item, list):
            print_list(item, level + 1)
        else:
            for tab in range(level):
                print("\t", end='')
            print(item)
