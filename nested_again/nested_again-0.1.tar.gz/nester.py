"""This module is to recursively go through a list
of items and any nested items."""

def print_lol(the_list):

    """This is the actual functions that assigns 'each_item'
to everything in the list.  Then uses if statement to
recursively go through 'each_item'"""
    for each_item in the_list:
        if isinstance(each_item, list):
	    print_lol(each_item)
        else:
            print(each_item)

