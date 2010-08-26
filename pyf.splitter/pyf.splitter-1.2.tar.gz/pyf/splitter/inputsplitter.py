"""inputsplitter module
"""

from pyjon.utils import get_secure_filename
import cPickle as pickle
import os

input_item_separator = '\x00'

class InputSplitterError(Exception):
    pass

class EndOfFileError(InputSplitterError):
    pass

def tokenize(buf, separator):
    items =  buf.split(separator)
    return_items = items[:-1]
    remainer = items[-1]
    return return_items, remainer

def get_input_item_str_flow(source_file,
        separator=input_item_separator, chunk_size=32768):
    """Low level function that should not be used as part as the public
    API.

    Used to read the raw data in the chunk files and feed the real
    get_input_item_flow function so that it can marshal the data
    """
    buf = ""
    # this gets reinitialized at the beginning of the loop
    newdata = "dummy"
    while newdata:
        newdata = source_file.read(chunk_size)
        buf += newdata
        items, buf = tokenize(buf, separator)
        for item in items:
            yield item

    if buf:
        raise EndOfFileError(
                'Bad file content: EOF reached but buffer not empty')

def get_input_item_flow(source_file, separator=input_item_separator, chunk_size=32768):
    """Yield Input Items from source_file file.
    @param: source_file: The open file that contain picklelized input items
    @type: source_file: FileObject
    The open file must be close by the caller.
    """
    for line in get_input_item_str_flow(source_file,
            separator=input_item_separator, chunk_size=chunk_size):
        yield pickle.loads(line)

def get_splitter(input_flow=None, max_items=200, split_node_name=None):
    """Function to instanciate the good splitter, if you want to use splitter
    with split_node_name parameter,
    the function instanciate a InputSplitterNode.
    If you want to use splitter without use split node name,
    the function instanciate a InputSplitterSingle
    """
    if split_node_name:
        splitter = InputSplitterNode(input_flow, max_items, split_node_name)
    else:
        splitter = InputSplitterSingle(input_flow, max_items)

    return splitter

class InputSplitterSingle(object):

    def __init__(self, input_flow=None, max_items=200):
        self.input_flow = input_flow
        self.max_items = max_items
        self.current_bucket = self.__get_new_bucket()
        self.buckets = list()

    def __get_new_bucket(self):
        self.current_bucket_size = 0
        file_obj = open(get_secure_filename(), 'wb')
        return file_obj

    def push(self, input_item):
        self.current_bucket.write(
                '%s%s' % (pickle.dumps(input_item), input_item_separator))
        
        bucket_filename = self.current_bucket.name

        self.current_bucket_size += 1
        if not self.max_items == 0 and self.current_bucket_size >= self.max_items:
            self.buckets.append(self.current_bucket.name)
            self.current_bucket.close()
            self.current_bucket = self.__get_new_bucket()
            
        return bucket_filename

    def split(self):
        for input_item in self.input_flow:
            self.push(input_item)
            
        return self.finalize()
    
    def finalize(self):
        self.current_bucket.close()
        if not self.current_bucket_size == 0:
            self.buckets.append(self.current_bucket.name)

        return self.buckets
           
class InputSplitterNode(object):

    def __init__(self, input_flow, max_items, split_node_name):
        """Initialize a new InputSplitter
        @param: input_flow: Flow of Input Items
        @type: generator of InputItems instances

        @param: max_items: Max Input Items to split
        @type: Integer
        
        @param split_node_name: The node name that we want to keep for a chunk.
        example : TransactionReference
        @type: String

        return a tuple of closed filenames containing InputItems picklelized
        """
        self.input_flow = input_flow
        self.max_items = max_items
        self.split_node_name = split_node_name

        # dictionnary indexed by reference value contain the number found of
        # reference value
        self.reference_size = dict()

        # dictionnary indexed by line number contain the reference value
        self.line_reference = dict()
        
        # dictionnary indexed by filename contain the file object
        self.bucket_files = dict()

        # dictionnary indexed by filename contain the number of line from the
        # file
        self.bucket_size = dict()

        # list of existing/available bucket filenames
        self.bucket_filenames = list()

        # dictionnary indexed by reference value contain bucket filename
        self.bucket_reference_value = dict()

    def __close_buckets(self):
        """Close all existing bucket files
        """
        for data_file in self.bucket_files.values():
            
            if not data_file.closed:
                data_file.close()

    def __open_bucket(self):
        """Open a new bucket and return the bucket filename
        """
        filename = get_secure_filename()
        self.bucket_filenames.append(filename)
        data_file = open(filename, 'wb')
        self.bucket_files[filename] = data_file
        self.bucket_size[filename] = 0

    def __choose_bucket(self, input_item_str, line_number):
        """Choose the bucket for the input item
        """
        reference_value = self.line_reference[line_number]
        ref_value_count = self.reference_size[reference_value]

        if not self.max_items == 0 and ref_value_count > self.max_items:
            msg = 'Too mamy reference values (%s) found for %s,' % (ref_value_count, reference_value)
            msg += 'you may increase the max_items parameter'
            raise InputSplitterError(msg)

        for bucket_filename in self.bucket_filenames:
            bucket_size = self.bucket_size[bucket_filename]
            if self.max_items == 0 or bucket_size + ref_value_count <= self.max_items:
                self.bucket_reference_value[reference_value] = bucket_filename
                self.bucket_size[bucket_filename] += ref_value_count
                return bucket_filename
            else:
                bucket_file = self.bucket_files[bucket_filename]
                if not bucket_file.closed:
                    # close the bucket file because -> to many open files
                    bucket_file.close()

        # no enough space available
        self.__open_bucket()
        return self.__choose_bucket(input_item_str, line_number)

    def __store_input_item(self, input_item_str, line_number):
        """Store the Input item in the most appropriate bucket
        """
        reference_value = self.line_reference[line_number]

        if not self.bucket_reference_value.has_key(reference_value):
            bucket_filename = self.__choose_bucket(input_item_str, line_number)
        else:
            bucket_filename = self.bucket_reference_value[reference_value]

        file_obj = self.bucket_files[bucket_filename]

        tobeclosed = False
        if file_obj.closed:
            tobeclosed = True
            file_obj = open(bucket_filename, 'ab')
            self.bucket_files[bucket_filename] = file_obj

        self.store_input_item(file_obj, input_item_str)
        if tobeclosed:
            file_obj.close()

    def __get_reference_value(self, input_item):
        """Retrieve the reference value for the item item
        Can raise InputSplitterError if input item does not have
        split_node attribute
        """
        if not hasattr(input_item, self.split_node_name):
            raise InputSplitterError('Input item does not have attribute %s' % \
                self.split_node_name)

        ref_value = getattr(input_item, self.split_node_name)
        return ref_value

    def __check_references(self):
        max_size = 0
        max_ref_value = None
        for ref_value in self.reference_size.keys():
            ref_size = self.reference_size[ref_value]
            if ref_size > max_size:
                max_size = ref_size
                max_ref_value = ref_value


        if max_size > self.max_items:
            msg = 'Too mamy reference values (%s) found for %s,' % (max_size, max_ref_value)
            msg += 'you may increase the max_items parameter'
            raise InputSplitterError(msg)

    def __save_reference(self, reference_value, linenumber):
        """Save references for the input items
        """
        if not self.reference_size.has_key(reference_value):
            self.reference_size[reference_value] = 0

        self.reference_size[reference_value] += 1
        self.line_reference[linenumber] = reference_value

    def __prepare(self, input_flow):
        """Make the first pass, Load all Input Item and create a data structure
        with all references.
        """
        filename = get_secure_filename()
        file_data = open(filename, 'wb')
        line_number = 0
        for input_item in input_flow:
            line_number += 1
            reference_value = self.__get_reference_value(input_item)
            self.store_input_item(file_data, pickle.dumps(input_item))
            self.__save_reference(reference_value, line_number)

        file_data.close()

        if not self.max_items == 0:
            self.__check_references()

        return filename

    def store_input_item(self, source_file, input_item_str,
            separator=input_item_separator):
        source_file.write('%s%s' % (input_item_str, separator))
    
    def split(self):
        filename = self.__prepare(self.input_flow)
        data_file = open(filename, 'rb')
        line_number = 0
        for input_item_str in get_input_item_str_flow(data_file):
            line_number += 1
            self.__store_input_item(input_item_str, line_number)

        data_file.close()

        os.remove(filename)
        self.__close_buckets()
        return self.bucket_filenames

