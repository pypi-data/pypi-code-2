from attributemapper import AttributeMapper
import uuid

class File(AttributeMapper):
    """a ``File`` is the combination of a file and some metadata"""
    
    _filter_out=['fp','id_']
    
    def __init__(self, fp, asset_id=None, md={}):
        """initialize the Asset with a file pointer ``fp``, an ``asset_id`` which is a string
        and an metadata dictionary in ``md``.
        """
        
        if asset_id is None:
            asset_id=unicode(uuid.uuid4())
        
        super(File, self).__init__()

        self.fp = fp
        self.update(md)
        self.id_ = asset_id
    
    # make sure the fp is not stored in the dictionary    
    def _fp_get(self):
        return self.__fp
    
    def _fp_set(self, fp):
        self.__fp = fp
        
    #fp = property(_fp_get, _fp_set)
    
    

class ExtendedFileStore(object):
    """store and retrieve assets which are combinations of a file and metadata"""
    
    def __init__(self, filestore, mdstore):
        """initialize the ExtendedFileStore with a ``filestore`` and a ``mdstore``
        for storing the metadata"""
        
        self.filestore = filestore
        self.mdstore = mdstore
        
    def add(self, fobj):
        """add an file object to the manager meaning to add it to both storages. 
        ``fobj`` needs to be an instance of ``File``. The ``asset_id`` of that ``File`` 
        instance will be replaced by the asset id the filesystem store computes. Thus it 
        might be completely different from the original. If you need the original you need
        to store it as a different key in the metadata set."""
        aid = fobj.asset_id = self.filestore.add(fobj.fp,fobj.id_)
        self.mdstore.add(dict(fobj))
        return fobj.asset_id
        
    def __getitem__(self, asset_id):
        """return an asset by it'a asset id"""
        file = self.filestore[asset_id]
        md = self.mdstore.find({'asset_id': asset_id})[0] # TODO: shouldn't this be the internal id?
        return File(file, md=md)
        
    def update(self, fobj):
        """update a file object"""
        # TODO: implement
        
    def delete(self, asset_id):
        """delete a file by it's id"""
        self.filestore.delete(asset_id)
        self.mdstore.delete(asset_id)

    def find(self, query, sort_query=None, limit=None):
        """return assets which match the metadata query"""
        # TODO: write test for it
        md = self.mdstore
        md_items = md.find(query)
        if sort_query is not None:
            md_items = md_items.sort(sort_query)
        if limit is not None:
            md_items = md_items.limit(limit)

        # TODO: Make this an iterator
        r=[]
        for md in md_items:
            r.append(self[md['asset_id']])
        return r
