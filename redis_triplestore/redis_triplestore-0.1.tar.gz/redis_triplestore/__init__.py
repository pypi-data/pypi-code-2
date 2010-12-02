from redis_wrap import get_hash, get_set

class Namespace(object):
    def __init__(self, base_uri):
        self.base_uri = base_uri
    
    def __getattr__(self, name):
        return self.base_uri+name


class Resource(object):
    def __init__(self, uri, system='default', **data):
        self.uri = uri
        self.system = system
        hash = get_hash(uri, system)
        for k, v in data.items():
            hash[k] = v
        self.__dict__.update(dict(zip(hash.keys(), hash.values())))
    
    def __str__(self):
        return self.uri

    def __repr__(self):
        return "<Resource %s>" % self.__str__()
    
    def __cmp__(self, other):
        return self.uri==other.uri and 0

    def __getitem__(self, name):
        return get_hash(self, self.system).get(name)

    def relations(self, predicate):
        rels = get_set('rel:%s_%s' % (self, predicate), self.system)
        return [Resource(rel) for rel in rels]

    def reversed_relations(self, predicate):
        revs = get_set('rev:%s_%s' % (self, predicate), self.system)
        return [Resource(rev) for rev in revs]

    def delete_relation(self, predicate, object):
        rels = get_set('rel:%s_%s' % (self, predicate), self.system)
        rels.remove(object)
        revs = get_set('rev:%s_%s' % (object, predicate), self.system)
        revs.remove(self)

    def add_relation(self, predicate, object):
        rels = get_set('rel:%s_%s' % (self, predicate), self.system)
        rels.add(object)
        revs = get_set('rev:%s_%s' % (object, predicate), self.system)
        revs.add(self)

    def remove(self):
        hash = get_hash(self, self.system)
        for key in hash.keys():
            del hash[key]


if __name__ == "__main__":
    FOAF = Namespace('http://xmlns.com/foaf/0.1/')
    
    # Attribution
    frodo = Resource('http://example.com/comte/frodo', **{
        FOAF.name: 'Frodo',
        FOAF.familyName: 'Baggins',
    })
    assert frodo[FOAF.name] == 'Frodo'
    
    # Persistence
    frodo = Resource('http://example.com/comte/frodo')
    assert frodo[FOAF.name] == 'Frodo'
    
    gandalf = Resource('http://example.com/wizards/gandalf', **{
        FOAF.name: 'Gandalf',
        FOAF.familyName: 'the White',
    })
    saruman = Resource('http://example.com/wizards/saruman', **{
        FOAF.name: 'Saruman',
        FOAF.familyName: 'of Many Colors',
    })
    
    # Relations
    frodo.add_relation(FOAF.knows, gandalf)
    assert frodo.relations(FOAF.knows) == [gandalf]
    gandalf.add_relation(FOAF.knows, saruman)
    assert gandalf.relations(FOAF.knows) == [saruman]
    assert gandalf.reversed_relations(FOAF.knows) == [frodo]
    frodo.add_relation(FOAF.knows, saruman)
    assert frodo.relations(FOAF.knows) == [gandalf, saruman]
    
    # Clean up
    frodo.delete_relation(FOAF.knows, saruman)
    assert frodo.relations(FOAF.knows) == [gandalf]
    frodo.delete_relation(FOAF.knows, gandalf)
    gandalf.delete_relation(FOAF.knows, saruman)
    assert gandalf.relations(FOAF.knows) == []
    assert gandalf.reversed_relations(FOAF.knows) == []
    frodo.remove()
    gandalf.remove()
    saruman.remove()
    assert frodo[FOAF.name] == None
    
