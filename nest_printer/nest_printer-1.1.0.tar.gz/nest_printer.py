def print_lol(my_list, tabs=0):
	for item in my_list:
		if isinstance(item, list):
			print_lol(item, tabs+1)
		else:
			for i in range(tabs):
				print("\t", end='')

			print(item)


