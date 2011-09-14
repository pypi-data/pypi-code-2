from exceptions import Exception


class HeccerAddressError(Exception):
    """

    """
    def __init__(self, serial, field, msg=""):
        
        self.msg = "Cannot find the address of " + str(serial) + " -> " + field

        if msg != "":
            
            self.msg += ", %s" % msg
    
    def __str__(self):
        return self.msg


class HeccerNotAllocatedError(Exception):
    """

    """
    def __init__(self,msg):
        self.msg = msg
    
    def __str__(self):

        error_msg = "The Heccer core data struct is not allocated\n %s : %s" % (self.msg, self.value)
        
        return error_msg

class HeccerOptionsError(Exception):
    """

    """
    def __init__(self,msg):
        self.msg = msg
    
    def __str__(self):

        error_msg = "Error in the Heccer options\n %s : %s" % (self.msg, self.value)
        
        return error_msg


class HeccerCompileError(Exception):
    """

    """
    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):

        error_msg = "Error compiling Heccer: %s" % (self.msg)
        
        return error_msg
