""" My first module """
def printxx (thelist, level ):
        for element in thelist:
                if (isinstance(element,list)):
                        printxx(element,level+1)
                else:
                        for tab in range(level):
                                print("\t", end="")
                        print(element)
