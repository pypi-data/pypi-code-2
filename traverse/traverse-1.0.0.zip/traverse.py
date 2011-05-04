"""Function to recursively print out elements in the list and also elements of
list within a list"""
def print_lol(the_list):
	for i in the_list:
		if (isinstance(i,list)):
			print_lol(i);
		else:
			print(i);
