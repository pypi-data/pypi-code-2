"""Contains fibn which returns nth fibonacci number"""
def fibn(n):
    """Returns nth fibonacci number"""
    if n>2:
        return fibn(n-1)+fibn(n-2)
    else:
        return 1

if __name__ == "__main__":
    n=input("Enter n ")
    print (fibn(int(n)))
