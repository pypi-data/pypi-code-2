movies = ['Doraemon','Tom&Jerry', ['Power Ranger',[2011,'Khang Nguyen']]]
def print_lol (the_list):
    for a_element in the_list:
        if(isinstance(a_element,list)):
            print_lol(a_element)
        else:
            print a_element
print_lol(movies)
