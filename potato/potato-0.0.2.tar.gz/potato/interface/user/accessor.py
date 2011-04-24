
from zope.interface import Attribute
from potatoe.interface.base.verify import IVerifiable

class ITextFileAccessor(IVerifiable):
    """
    An object which is able to provide both the path to 
    a file and the ability to get the contents of this 
    file.
    """
    path = Attribute("""The path that the text file exists on""")
    contents = Attribute("""The contents of the text file.""")
    
    
    def contents():
        """
        Returns the contents of the file.
        """
    def open(file_access_details):
        """
        open the connection to the file.
        """
    def close():
        """
        close the connection to the file.
        """
    def __enter__(file_access_details):
        """
        Opens the file and keeps it open. 
        """
    def __exit__():
        """
        Closes and destroys the connection to the file.
        """

class ICommaSeperatedValueFileAccessor(ITextFileAccessor):
    """
    """

    __fields__ = Attribute("The list of fields available in this file.")

    def fields():
        """
        The list of fields available in this file.
        """
    def to_dictionary_list():
        """
        Returns a list of dictionaries where the keys are the field 
        names and the values are the actual values in that row. 
        """
    def to_tuples():
        """
        Returns a tuple of tuples of all the data.
        """
    
class IDataAccessor(IVerifiable):
    """
    An object which is able to provide access to data.
    """

    __conn__ = Attribute("The connection being used to access the data.")
    __conn_details__ = Attribute("The details used to create the connection.")

    def get(request, *args , **kwargs ):
        """
        Gets an object based on the request.
        """
    def update(request, *args , **kwargs ):
        """
        Updates the object based on the request.
        """
    def insert(request, *args , **kwargs ):
        """
        Inserts the object based on the request.
        """
    def delete(request, *args , **kwargs ):
        """
        Deletes the object based on the request.
        """
    def connect(connection_details, *args , **kwargs ):
        """
        Connects to the data store.
        """
    def disconnect():
        """
        Disconnects from the data store.
        """
    def __enter__(connection_details):
        """
        Creates the connection to the data store and opens it.
        """
    def __exit__():
        """
        Closes and destroys the connection to the data store.
        """

