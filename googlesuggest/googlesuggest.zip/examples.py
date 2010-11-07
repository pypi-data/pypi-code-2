from GoogleSuggest import GoogleSuggest

def example1():
    GS = GoogleSuggest("google")
    GS.read()
    for item in GS.suggest:
        print item

def example2():
    suggestions = GoogleSuggest("google").read()
    for suggest in suggestions:
        print suggest

def example3():
    suggestions = GoogleSuggest().read("google")
    for suggest in suggestions:
        print suggest


print "Example 1:\n"
example1()
print "\n\nExample 2:\n"
example2()
print "\n\nExample 3:\n"
example3()
