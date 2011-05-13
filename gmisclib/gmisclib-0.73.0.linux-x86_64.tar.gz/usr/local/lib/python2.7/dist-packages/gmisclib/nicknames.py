


def nicknames(namelist):
	"""Takes a list of names and trims off junk from the beginning
	and ends of the names to produce a set of reasonable nicknames
	that are relatively compact and easy to read.

	It returns a map from the names to the nicknames, along with
	the stuff trimmed off from the edges.
	"""

	namelist = list(namelist)
	assert len(namelist) > 0
	left = ''
	right = ''
	ll = 1
	while ll <= len(namelist[0]):
		left = namelist[0][:ll]
		failed = False
		for nm in namelist:
			if not nm.startswith(left):
				failed = True
				break
		if failed:
			ll -= 1
			left = left[:ll]
			break
		ll += 1
	rr = 1
	while rr <= len(namelist[0]):
		right = namelist[0][-rr:]
		failed = False
		for nm in namelist:
			if not nm[ll:].endswith(right):
				failed = True
				break
		if failed:
			right = right[1:]
			rr -= 1
			break
		rr += 1
	map = {}
	for nm in namelist:
		map[nm] = nm[ll:len(nm)-rr]
	return (map, left, right)



def test():
	m, l, r = nicknames(['football.', 'fooberry.', 'fools gold.'])
	assert l == 'foo'
	assert r == '.'
	mi = m.items()
	mi.sort()
	assert mi == [('fooberry.', 'berry'), ('fools gold.', 'ls gold'), ('football.', 'tball')]
	assert l + m['football.'] + r == 'football.'

	m, l, r = nicknames(['abc', 'def'])
	assert l=='' and r==''
	assert m['abc'] == 'abc'
	assert l + m['abc'] + r == 'abc'

	m, l, r = nicknames(['abc'])
	assert l + m['abc'] + r == 'abc'

	m, l, r = nicknames(['val', 'str'])
	print m, l, r




if __name__ == '__main__':
	test()
