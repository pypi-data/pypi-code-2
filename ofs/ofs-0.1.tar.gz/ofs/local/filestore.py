'''The simplest possible store you could imagine.'''
from ofs.base import OFSInterface

class LocalFileOFS(OFSInterface):
    def __init__(self, storage_dir='ofsdata'):
        self.storage_dir = storage_dir

    def _path(self, bucket, label):
        return os.path.join(self.storage_dir, bucket, label)

    def exists(bucket, label):
        return os.
        raise NotImplementedError

    def claim_bucket(self, bucket):
        '''Claim a bucket.

        :return: True if successful, False otherwise.
        '''
        raise NotImplementedError

    def list_labels(self, bucket):
        '''List labels for the given bucket.

        :param bucket: bucket to list labels for.
        :return: iterator for the labels in the specified bucket.
        '''
        raise NotImplementedError
    
    def list_buckets(self):
        '''List all buckets managed by this OFS instance.
        
        :return: iterator for the buckets.
        '''
        raise NotImplementedError

    def get_stream(self, bucket, label, as_stream=True):
        '''Get a bitstream for the given bucket:label combination.

        :param bucket: the bucket to use.
        :return: bitstream as a file-like object 
        '''
        raise NotImplementedError

    def put_stream(self, bucket, label, stream_object, params={}):
        '''Put a bitstream (stream_object) for the specified bucket:label identifier.

        :param bucket: as standard
        :param label: as standard
        :param stream_object: file-like object to read from.
        :param params: update metadata with these params (see `update_metadata`)
        '''
        raise NotImplementedError

    def del_stream(self, bucket, label):
        '''Delete a bitstream.
        '''
        raise NotImplementedError

    def get_metadata(self, bucket, label):
        '''Get the metadata for this bucket:label identifier.
        '''
        raise NotImplementedError

    def update_metadata(self, bucket, label, params):
        '''Update the metadata with the provided dictionary of params.

        :param parmams: dictionary of key values (json serializable).
        '''
        raise NotImplementedError

    def del_metadata_keys(self, bucket, label, keys):
        '''Delete the metadata corresponding to the specified keys.
        '''
        raise NotImplementedError

