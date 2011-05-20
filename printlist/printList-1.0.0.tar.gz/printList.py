"""This is "nester.py" module, and it provides one function called printListOfList method,
hich prints each element of the main list & corresponding nested list using recursion."""

def printListOfList(theList):
    for eachElement in theList:
        if isinstance(eachElement, list):
            printListOfList(eachElement)

        else:
            print(eachElement)
