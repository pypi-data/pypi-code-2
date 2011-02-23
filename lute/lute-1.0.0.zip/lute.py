def lute(lol):
    for x in lol:
        if isinstance(x,list):
            lute(x)
        else:
            print(x,end='')
