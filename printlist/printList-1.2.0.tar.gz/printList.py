"""This is "nester.py" module, and it provides one function called printListOfList method,
hich prints each element of the main list & corresponding nested list using recursion.
theList - List ot be printed
indent - indicates whether nested list should be intended or not
level - number of tab"""

def printListOfList(theList, indent=False,level=0):
    for eachElement in theList:
        if isinstance(eachElement, list):
            printListOfList(eachElement, indent, level+1)

        else:
            if indent:
                for indent in range(level):
                    print("\t", end='')
            print(eachElement)
