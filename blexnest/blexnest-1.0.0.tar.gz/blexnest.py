#The Nester module from HFPython.

def print_lol(the_list):
    for each_line in the_list:
        if isinstance(each_line, list) == True:
            print_lol(each_line)
        else:
            print(each_line)
