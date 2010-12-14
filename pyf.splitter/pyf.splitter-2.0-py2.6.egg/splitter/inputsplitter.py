""" Low-level item flow splitting, used to save on hard disk data flows in separate reusable buckets.
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
    
    :param source_file: The open file that contain picklelized input items
    :type source_file: FileObject

    The open file must be close by the caller.
    """
    for line in get_input_item_str_flow(source_file,
            separator=input_item_separator, chunk_size=chunk_size):
        yield pickle.loads(line)

def chain_splitters(input_flow, splitters_params, separator=input_item_separator):
    """Allow to chain splitters. Each splitter (except for the first one
    obviously) will have as input the output of the previous one, a bit
    like how  commands are piped in a Unix shell.

    :param input_flow: the flow of items to split
    :type input_flow: iterator

    :param separator: the item separator in **all** splitters
    :type separator: string

    :param splitters_params: the parameters to pass to each splitter
    :type splitters_params:  list of dictionaries

    The `separator` obviously needs to be the same for all splitters, since
    each one will take as input the output of the previous one.

    The `splitters_params` is a list of dictionaries. Each dictionary
    represents the parameters to pass to each splitter. They are the same as
    accepted by the `get_splitter` function.

    As an example, take the following list::

        [{'split_attribute': 'field1'},
         {'split_attribute': 'field2', 'force_split': True}]

    This means that the `input_flow` will first be splitted by an
    `InputSplitterByAttribute` based on the `field1` attribute of each item,
    and then each split flow will be splitted again by a second
    `InputSplitterByAttribute` based on the `field2` attribute of each item,
    making sure that this time any two items with a different value for their
    `field2` attribute will **not** remain together.
    """
    def dump_input_flow(input_flow, separator):
        """Dump all the items in a file."""
        filename = get_secure_filename()
        file_data = open(filename, 'wb')

        for item in input_flow:
            file_data.write('%s%s' % (pickle.dumps(item), separator))

        file_data.close()
        return filename

    def do_split(input_filenames, params):
        """Actually split."""
        output_filenames = list()

        for filename in input_filenames:
            f = open(filename, 'rb')
            params['input_flow'] = get_input_item_flow(f)

            output_filenames.extend(get_splitter(**params).split())

            f.close()

        return output_filenames

    # bootstrap the process: all iterations take a list of files as input
    filenames = list()
    filenames.append(dump_input_flow(input_flow, separator))

    for splitter_params in splitters_params:
        filenames = do_split(filenames, splitter_params)

    return filenames

def get_splitter(input_flow=None, max_items=200, split_attribute=None,
        force_split=False):
    """Function to instanciate the adequate splitter, whether you want to:

    * just split the `input_flow` of items into buckets of a `max_items`
      maximum size with the `InputSplitterSingle`
    * use the `InputSplitterByAttribute` to guarantee that two items from the
      `input_flow` with the same value for their `split_attribute` attribute
      **will not** be separated into different buckets. You might optionally
      want to guarantee that two items with a different value for their
      `split_node` attribute **will** be separated.
    """
    if split_attribute:
        splitter = InputSplitterByAttribute(input_flow, max_items,
                split_attribute, force_split)
    else:
        splitter = InputSplitterSingle(input_flow, max_items)

    return splitter

class InputSplitterSingle(object):
    """ Simple splitter, without special rules """

    def __init__(self, input_flow=None, max_items=200):
        self.input_flow = input_flow
        self.max_items = max_items
        self.current_bucket = self.get_new_bucket()
        self.buckets = list()

    def get_new_bucket(self):
        """ This method shouldn't be used outside of the implementation. """
        self.current_bucket_size = 0
        file_obj = open(get_secure_filename(), 'wb')
        return file_obj

    def push(self, input_item):
        """ Permits to push a single item in the splitter, returning the corresponding bucket """
        self.current_bucket.write(
                '%s%s' % (pickle.dumps(input_item), input_item_separator))
        
        bucket_filename = self.current_bucket.name

        self.current_bucket_size += 1
        if not self.max_items == 0 and self.current_bucket_size >= self.max_items:
            self.buckets.append(self.current_bucket.name)
            self.current_bucket.close()
            self.current_bucket = self.get_new_bucket()
            
        return bucket_filename

    def split(self):
        """ Launches the splitting and finalizes it, returning the buckets """
        for input_item in self.input_flow:
            self.push(input_item)
            
        return self.finalize()
    
    def finalize(self):
        """ Finalizes the splitter, and returns the buckets """
        self.current_bucket.close()
        if not self.current_bucket_size == 0:
            self.buckets.append(self.current_bucket.name)

        return self.buckets

class InputSplitterByAttribute(object):
    """This splitter guarantees that any two items with the same value for a
    certain attribute (called `split_attribute`) will not be separated.

    The normal behavior is to try and group items that have a different
    `split_attribute` value into the same bucket when possible, unless the
    `force_split` parameter is set to `True`.
    
    If that makes a given group bigger than the desired max number of items, it
    raises `InputSplitterError`.

    :param input_flow: Flow of items to split
    :type input_flow: generator

    :param max_items: Max number of items in a group
    :type max_items: Integer
        
    :param split_attribute: The attribute name for which equal values will not be separated
    :type split_attribute: String

    :param force_split: Do not group items with different `split_attribute` values if `True`
    :param force_split: boolean
    """

    def __init__(self, input_flow, max_items, split_attribute, force_split):
        self.input_flow = input_flow
        self.max_items = max_items
        self.split_attribute = split_attribute
        self.force_split = force_split

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

    def __open_bucket(self, reference_value, ref_value_count):
        """Open a new bucket and return the bucket filename
        """
        filename = get_secure_filename()
        self.bucket_filenames.append(filename)

        data_file = open(filename, 'wb')
        self.bucket_files[filename] = data_file
        self.bucket_size[filename] = ref_value_count
        self.bucket_reference_value[reference_value] = filename

        return filename

    def __choose_bucket(self, input_item_str, line_number):
        """Choose the bucket for the input item
        """
        reference_value = self.line_reference[line_number]
        ref_value_count = self.reference_size[reference_value]

        # Value counts were already checked in the __check_references function.
        # Unfortunately, some items can be pushed directly through the
        # store_input_item funtion. As long as the latter can be called
        # directly and publicly, then we need to check it again here.
        if not self.max_items == 0 and ref_value_count > self.max_items:
            msg = 'Too many reference values (%s) found for %s,' % (ref_value_count, reference_value)
            msg += 'you may increase the max_items parameter'
            raise InputSplitterError(msg)

        if not self.force_split:
            # see if we can reuse another one
            for bucket_filename in self.bucket_filenames:
                bucket_size = self.bucket_size[bucket_filename]
                if self.max_items == 0 or (bucket_size + ref_value_count) <= self.max_items:
                    # let's reuse this bucket
                    self.bucket_reference_value[reference_value] = bucket_filename
                    self.bucket_size[bucket_filename] += ref_value_count
                    return bucket_filename

                else:
                    # chances are we won't be able to reuse this bucket,
                    # close it to avoid the infamous "too many open files" error
                    bucket_file = self.bucket_files[bucket_filename]
                    if not bucket_file.closed:
                        bucket_file.close()

        # let's use a new bucket
        bucket_filename = self.__open_bucket(reference_value, ref_value_count)

        return bucket_filename

    def __store_input_item(self, input_item_str, line_number):
        """Store the Input item in the most appropriate bucket
        """
        reference_value = self.line_reference[line_number]

        if self.bucket_reference_value.has_key(reference_value):
            bucket_filename = self.bucket_reference_value[reference_value]
        else:
            bucket_filename = self.__choose_bucket(input_item_str, line_number)

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
        """Retrieve the reference value for the input item.

        Can raise an `InputSplitterError` if input item does not have the
        `split_attribute` attribute.
        """
        if not hasattr(input_item, self.split_attribute):
            raise InputSplitterError('Input item does not have a %s attribute'
                    % self.split_attribute)

        ref_value = getattr(input_item, self.split_attribute)
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
            msg = 'Too many reference values (%s) found for %s,' % (max_size, max_ref_value)
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
        """Make the first pass: load all input items and create a data
        structure with all references.
        """
        filename = get_secure_filename()
        file_data = open(filename, 'wb')

        for line_number, input_item in enumerate(input_flow):
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
        """ Launches the splitting, returning bucket filenames in an array. """
        filename = self.__prepare(self.input_flow)

        data_file = open(filename, 'rb')
        for line_number, input_item_str in enumerate(get_input_item_str_flow(data_file)):
            self.__store_input_item(input_item_str, line_number)

        data_file.close()
        os.remove(filename)
        self.__close_buckets()

        return self.bucket_filenames

