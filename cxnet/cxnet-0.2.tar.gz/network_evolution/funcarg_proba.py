def func(first, second, third=3):
    print "First: '%s'\nSecond: '%s',\nThird: '%s'\n" % (first, second, third)

args = ("arg1", "arg2")
func(*args)

kw= {"first": 1, "second": 2, "third": "harom"}
func(**kw)

kw2= {"third": "harom"}
func(*args, **kw2)

#Ez nem mukodik:
func(*args, **kw)
#mert tobbszor vannak argumentumok definialva.
