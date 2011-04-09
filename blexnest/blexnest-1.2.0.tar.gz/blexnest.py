#The Nester module from HFPython.

def print_lol(the_list, level=0):
    for each_line in the_list:
        if isinstance(each_line, list) == True:
            print_lol(each_line, level+1)
        else:
            print(each_line)
