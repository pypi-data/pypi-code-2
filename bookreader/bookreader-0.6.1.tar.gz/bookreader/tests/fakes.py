from oaipmh.tests.fakeclient import FakeClient 
from bookreader.models import Repository



    
    

def fake_repository_connection(repository, mapping):
    def fake_connection(**kwargs):
        conn = Repository.connection(repository, **kwargs)
        old_oai = conn.oai
        conn.oai = FakeClient(mapping)
        conn.oai._metadata_registry = old_oai._metadata_registry
        
        return conn
    
    repository.connection = fake_connection
