#This is the "print_list" module, which contains the print_list() function.
#print_list() makes it possible to spot lists within lists and print them propperly.

def print_list(target):
	
	#This function finds any python list within other lists. Then, the function prints all found data items within the lists and prints them recursively on the screen, one item on each line.
	for item in target:	
		if isinstance(item, list):
			print_list(item)
		
		else:
			print(item)
