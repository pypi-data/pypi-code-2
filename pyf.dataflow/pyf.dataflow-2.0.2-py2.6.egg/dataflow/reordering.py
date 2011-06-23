from pyjon.utils import get_secure_filename

try:
    import cPickle as pickle
except ImportError:
    import pickle
    
import itertools
import operator
import os
    
apickle = type('pickler', (), {})()
apickle.loads = pickle.loads
apickle.dumps = lambda v: pickle.dumps(v, -1)

def reorder_flow(iterator, key, continue_val=None, serializer=apickle):
    """ `New in version 2.0.1`
    
    Reorders a serializable flow according to a specific key:
    works like sorted(iterator, key=key).
    
    It serializes the flow to a temporary file while indexing the gotten keys
    and replays the flow in an ordered way.
    
    Default serializer is pickle with latest protocol version.
    
    :param iterator: The iterator to reorder
    :param key: The key getter (ex: "`operator.attrgetter('blah')`", "`lambda v: v[1]`")
    :type key: callable
    :param continue_val: If specified, the function will yield the passed item each time it
    receives an item without yielding one.
    :param serializer: Serializer override (usefull to set "marshal" or "json"/"simplejson" for example instead of pickle
    :type serializer: Object (likely module) with "loads" and "dumps" callable attributes.
    """
    line_offsets = []
    line_keys = dict()
    offset = 0
    
    filename = get_secure_filename()
    write_file = open(filename, 'wb')
    cur_buffer = ""
    for i, item in enumerate(iterator):
        item_content = serializer.dumps(item)
        line_offsets.append(offset)
        line_keys[i] = key(item)
        
        offset += len(item_content)
        
        #write_file.write(item_content)
        cur_buffer += item_content
        
        if continue_val is not None:
            yield continue_val
            
        if not i % 100:
            write_file.write(cur_buffer)
            cur_buffer = ""
    
    write_file.write(cur_buffer)
    cur_buffer = ""
    write_file.close()
    
    read_file = open(filename, 'rb')
    lines_ordered = itertools.imap(operator.itemgetter(0),
                                   sorted(line_keys.items(),
                                          key=operator.itemgetter(1)))
    line_count = len(line_offsets)
    
    for line in lines_ordered:
        read_file.seek(line_offsets[line])
        if line_count > (line + 1):
            yield serializer.loads(read_file.read(line_offsets[line+1] - line_offsets[line]))
        else:
            yield serializer.loads(read_file.read())
    read_file.close()
    os.unlink(filename)