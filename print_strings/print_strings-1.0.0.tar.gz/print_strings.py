def print_the_strings(some_list):
        for each_item in some_list:
                if isinstance(each_item, str):
                        print(each_item, end="\t")
