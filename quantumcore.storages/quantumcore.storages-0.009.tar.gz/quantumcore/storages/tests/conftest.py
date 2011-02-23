import pkg_resources
import quantumcore.storages as storages
import py

plugins=["tmpdir"]

IMAGE1 = pkg_resources.resource_filename(__name__,"data/quantumcore.png")
IMAGE2 = pkg_resources.resource_filename(__name__,"data/comlounge.jpg")

def pytest_funcarg__file(request):
    return request.cached_setup(
             setup=lambda: open(IMAGE1),
             teardown=lambda val: val.close(),
             scope="function"
    )

def pytest_funcarg__file2(request):
    return request.cached_setup(
             setup=lambda: open(IMAGE2),
             teardown=lambda val: val.close(),
             scope="function"
    )

def pytest_funcarg__fs(request):
    """return a filesystem storage"""
    tmpdir = request.getfuncargvalue("tmpdir")
    filestorage = storages.FilesystemStore(str(tmpdir), "/%Y/%m")
    return filestorage
    
def pytest_funcarg__md(request):
    """return a metadata storage"""
    return storages.MemoryMappingStore('asset_id')
            
def pytest_funcarg__efs(request):
    fs = request.getfuncargvalue("fs")
    md = request.getfuncargvalue("md")
    return storages.ExtendedFileStore(fs,md)

def pytest_funcarg__asset_id(request):
    return 3
    

### 
### helpers for mongodb tests
###
 
def pytest_addoption(parser):
    parser.addoption('--mongodb-uri', default="mongodb://localhost", dest="mongodb_uri",
                      help='The connection URI for the MongoDB connection.')

    parser.addoption('--mongodb-name', default="_______foobar______", dest="mongodb_name",
                      help='Name of the test database to use for the mongodb tests. Note that this database will be dropped after the tests!')
   
def setup_mongo():
    uri = py.test.config.getvalue("mongodb_uri")
    name = py.test.config.getvalue("mongodb_name")

    import pymongo
    try:
        conn = pymongo.Connection.from_uri(uri)
    except pymongo.errors.AutoReconnect:
        py.test.skip("MongoDB database connection couldn't be established")
    db = conn[name]
    coll = db.test
    return storages.MongoMappingStore(coll)
    
def teardown_mongo(store):
    """drop the database contents again"""
    name = py.test.config.getvalue("mongodb_name")
    store.coll.database.connection.drop_database(name)
        
def pytest_funcarg__mongostore(request):
    return request.cached_setup(
            setup=setup_mongo,
            teardown=teardown_mongo,
            scope="module"
        )
    
    
    
    
    
