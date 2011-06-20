"""This is Rec_GetUserInput.py module.It gets the user input to start 
    Device inventory program for checking in or checking out.
    This module is recursive until user enter proper option or type exit"""
def Rec_GetUserInput():
    print"Welcome to Device Inventory Program.\nTo quite this program write exit any time"
    UserOption = raw_input("Please type 'i' for check in or 'o' for check out \n")
    if UserOption.lower() == 'i':
        print 'You have choose check in option'
        raw_input("Thanks press<enter>")
    elif UserOption.lower()==  'o':
        print "You have choose check out option"
        raw_input("Thanks press<enter>")
    elif UserOption.lower() == 'exit':
        print"You are exiting from this program"
        return 
    else:
        Rec_GetUserInput()
            


#Rec_GetUserInput()
