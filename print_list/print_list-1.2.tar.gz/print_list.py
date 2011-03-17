#This is the "print_list" module, which contains the print_list() function.
#print_list() makes it possible to spot lists within lists and print them propperly.
#As of 1.2 you can choose if you want to indent each list in a new tab-stop.

def print_list(target, indent=False, level=0):	
	#This function finds any python list within other lists.
	#IF you specify inden to true; then each list will have its own indent level
	#IF you use indent you can specify the lowest indent value in the level arg.
	
	for item in target:	
		if isinstance(item, list):
			print_list(item, indent, level+1)
		else:
			if indent:
				print("\t"*level, end="")
				"""To use this formula instead of a loop will increas preformance. The amont of preformence loss in a loop is minimal anyways"""
			print(item)
