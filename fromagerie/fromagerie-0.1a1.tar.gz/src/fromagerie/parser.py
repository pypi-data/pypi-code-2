from django.http.multipartparser import MultiPartParser, LimitBytes,\
    LazyStream, ChunkIter, FIELD, RAW, FILE, StopFutureHandlers,\
    MultiPartParserError, exhaust, InputStreamExhausted, StopUpload,\
    parse_header
from django.http.multipartparser import InterBoundaryIter as OldInterBoundaryIter
from django.http.multipartparser import BoundaryIter as OldBoundaryIter
from django.utils.text import unescape_entities
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import force_unicode

class DistutilsMultiPartParser(MultiPartParser):
    """
    Handle POST data from distutils if necessary.
    """

    def parse(self):
        """
        Parse the POST data and break it into a FILES MultiValueDict and a POST
        MultiValueDict.

        Returns a tuple containing the POST and FILES dictionary, respectively.
        """
        # We have to import QueryDict down here to avoid a circular import.
        from django.http import QueryDict

        encoding = self._encoding
        handlers = self._upload_handlers

        limited_input_data = LimitBytes(self._input_data, self._content_length)


        # See if the handler will want to take care of the parsing.
        # This allows overriding everything if somebody wants it.
        for handler in handlers:
            result = handler.handle_raw_input(limited_input_data,
                                              self._meta,
                                              self._content_length,
                                              self._boundary,
                                              encoding)
            if result is not None:
                return result[0], result[1]

        # Create the data structures to be used later.
        self._post = QueryDict('', mutable=True)
        self._files = MultiValueDict()

        # Instantiate the parser and stream:
        stream = LazyStream(ChunkIter(limited_input_data, self._chunk_size))

        # Whether or not to signal a file-completion at the beginning of the loop.
        old_field_name = None
        counters = [0] * len(handlers)

        try:
            for item_type, meta_data, field_stream in Parser(stream, self._boundary):
                if old_field_name:
                    # We run this at the beginning of the next loop
                    # since we cannot be sure a file is complete until
                    # we hit the next boundary/part of the multipart content.
                    self.handle_file_complete(old_field_name, counters)
                    old_field_name = None

                try:
                    disposition = meta_data['content-disposition'][1]
                    field_name = disposition['name'].strip()
                except (KeyError, IndexError, AttributeError):
                    continue

                transfer_encoding = meta_data.get('content-transfer-encoding')
                field_name = force_unicode(field_name, encoding, errors='replace')

                if item_type == FIELD:
                    # This is a post field, we can just set it in the post
                    if transfer_encoding == 'base64':
                        raw_data = field_stream.read()
                        try:
                            data = str(raw_data).decode('base64')
                        except:
                            data = raw_data
                    else:
                        data = field_stream.read()

                    # trim leading and following whitespace
                    data = data.strip()

                    # distutils sets blank fields to 'UNKNOWN'
                    if data == 'UNKNOWN':
                        data = ''

                    self._post.appendlist(field_name,
                                          force_unicode(data, encoding, errors='replace'))
                elif item_type == FILE:
                    # This is a file, use the handler...
                    file_name = disposition.get('filename')

                    if not file_name:
                        continue
                    file_name = force_unicode(file_name, encoding, errors='replace')

                    file_name = self.IE_sanitize(unescape_entities(file_name))


                    content_type = meta_data.get('content-type', ('',))[0].strip()
                    try:
                        charset = meta_data.get('content-type', (0,{}))[1].get('charset', None)
                    except:
                        charset = None

                    try:
                        content_length = int(meta_data.get('content-length')[0])
                    except (IndexError, TypeError, ValueError):
                        content_length = None

                    counters = [0] * len(handlers)
                    try:
                        for handler in handlers:
                            try:
                                handler.new_file(field_name, file_name,
                                                 content_type, content_length,
                                                 charset)
                            except StopFutureHandlers:
                                break

                        for chunk in field_stream:
                            if transfer_encoding == 'base64':
                                # We only special-case base64 transfer encoding
                                try:
                                    chunk = str(chunk).decode('base64')
                                except Exception, e:
                                    # Since this is only a chunk, any error is an unfixable error.
                                    raise MultiPartParserError("Could not decode base64 data: %r" % e)

                            for i, handler in enumerate(handlers):
                                chunk_length = len(chunk)
                                chunk = handler.receive_data_chunk(chunk,
                                                                   counters[i])
                                counters[i] += chunk_length
                                if chunk is None:
                                    # If the chunk received by the handler is None, then don't continue.
                                    break

                    except SkipFile, e:
                        # Just use up the rest of this file...
                        exhaust(field_stream)
                    else:
                        # Handle file upload completions on next iteration.
                        old_field_name = field_name
                else:
                    # If this is neither a FIELD or a FILE, just exhaust the stream.
                    exhaust(stream)
        except StopUpload, e:
            if not e.connection_reset:
                exhaust(limited_input_data)
        else:
            # Make sure that the request data is all fed
            exhaust(limited_input_data)

        # Signal that the upload has completed.
        for handler in handlers:
            retval = handler.upload_complete()
            if retval:
                break

        return self._post, self._files

def parse_boundary_stream(stream, max_header_size):
    """
    Parses one and exactly one stream that encapsulates a boundary.
    """

    # Stream at beginning of header, look for end of header
    # and parse it if found. The header must fit within one
    # chunk.
    chunk = stream.read(max_header_size)

    # 'find' returns the top of these four bytes, so we'll
    # need to munch them later to prevent them from polluting
    # the payload.
    header_end = chunk.find('\r\n\r\n')
    eat_bytes = 4

    if header_end == -1:
        header_end = chunk.find('\n\n')
        eat_bytes = 2
    

    def _parse_header(line):
        main_value_pair, params = parse_header(line)
        try:
            name, value = main_value_pair.split(':', 1)
        except:
            raise ValueError("Invalid header: %r" % line)
        return name, (value, params)

    if header_end == -1:
        # we find no header, so we just mark this fact and pass on
        # the stream verbatim
        stream.unget(chunk)
        return (RAW, {}, stream)

    header = chunk[:header_end]

    # here we place any excess chunk back onto the stream, as
    # well as throwing away the CRLFCRLF bytes from above.
    stream.unget(chunk[header_end + eat_bytes:])

    TYPE = RAW
    outdict = {}

    # Eliminate blank lines
    for line in header.split('\r\n'):
        # This terminology ("main value" and "dictionary of
        # parameters") is from the Python docs.
        try:
            name, (value, params) = _parse_header(line)
        except:
            continue

        if name == 'content-disposition':
            TYPE = FIELD
            if params.get('filename'):
                TYPE = FILE

        outdict[name] = value, params

    if TYPE == RAW:
        stream.unget(chunk)

    return (TYPE, outdict, stream)

class BoundaryIter(OldBoundaryIter):
    def __init__(self, stream, boundary):
        super(BoundaryIter, self).__init__(stream, boundary)
        self._rollback = len(boundary) + 4

class InterBoundaryIter(OldInterBoundaryIter):
    def next(self):
        try:
            return LazyStream(BoundaryIter(self._stream, self._boundary))
        except InputStreamExhausted:
            raise StopIteration()

class Parser(object):
    def __init__(self, stream, boundary):
        self._stream = stream
        self._separator = '--' + boundary

    def __iter__(self):
        boundarystream = InterBoundaryIter(self._stream, self._separator)
        for sub_stream in boundarystream:
            # Iterate over each part
            yield parse_boundary_stream(sub_stream, 1024)
