# import

from van.pydeb import main

def runit(string):
    "Test run a command"
    # find quoted argments:
    targs = string.split('"')
    count = 0
    args = []
    for arg in targs:
        if divmod(count, 2)[1] == 0:
            args.extend(arg.split())
        else:
            args.append(arg)
        count += 1
    exitcode = main(args)
    if exitcode != 0:
        return exitcode
