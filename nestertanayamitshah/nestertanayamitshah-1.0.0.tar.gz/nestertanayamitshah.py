def printnamestest (nameslist):
	for name in nameslist:
		if isinstance(name,list):
			printnamestest(name)
		else:
			print(name)
