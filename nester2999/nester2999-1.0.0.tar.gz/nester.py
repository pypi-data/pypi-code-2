"""This is “nester.py" module, and it provides one function called print_lol() which prints
lists that may or may not include nested lists."""

def print_tableau(liste):
	for each_item in liste:
		if isinstance(each_item,list):
			print_tableau(each_item)
		else:
			print(each_item)
