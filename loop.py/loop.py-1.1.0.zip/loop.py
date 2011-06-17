#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      DHARMESHBA
#
# Created:     09-06-2011
# Copyright:   (c) DHARMESHBA 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def main():
    pass

if __name__ == '__main__':
    main()
def dabbu(lame,level):
    for x in lame:
     if isinstance(x,list):
        dabbu(x,level+1)
     else:
        for tab_stop in range(level):
            print("\t")
        print x


