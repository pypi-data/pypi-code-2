#This is the "print_list" module, which contains the print_list() function.
#print_list() makes it possible to spot lists within lists and print them propperly.

def print_list(target, level):
	
	#This function finds any python list within other lists.
	#Then, the function prints all found data items within the lists and prints them recursively on the screen, one item on each line.
	#A second argument "level" is used to insert a tab-stop when a list in a list is discovered
	for item in target:	
		if isinstance(item, list):
			print_list(item, level+1)
		
		else:
			for tab in range(level):
				print("\t", end="")
			print(item)
