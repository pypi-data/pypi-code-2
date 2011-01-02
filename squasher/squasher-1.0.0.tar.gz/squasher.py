"""this is the "nester.py" module and it contains the function "print_lol" which prints lists and any nested lists"""

def print_lol(the_list):

        """this is a recursive function named "print_lol" which takes a positional argument called "the_list".
	Each item in the list is recursively printed on its own line."""
	
        for each_item in the_list:
                if isinstance(each_item, list):
                        print_lol(each_item)
                else:
                        print(each_item)

