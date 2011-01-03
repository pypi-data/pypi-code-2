"""this is the "squasher.py" module and it contains the function "print_lol" which prints lists and any nested lists"""

def print_lol(the_list, level):

        """this is a recursive function named "print_lol" which takes a positional argument called "the_list".
	Each item in the list is recursively printed on its own line. A second argument inserts tabs when a nested list
	is encoutered."""
	
        for each_item in the_list:
                if isinstance(each_item, list):
                        print_lol(each_item, list+1)
                else:
                        for tab_stop in range(level):
                        	print("\t", end = '')

