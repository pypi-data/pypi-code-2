"""
Generic methods to serialize models to and from yaml.
"""

import yaml

import dictserializer
from filters import Filter

def LoadValue(yamldata):
    return yaml.load(yamldata)

def SaveValue(val):
    return yaml.dump(val)

def LoadModel(yamldata, reqclsname=None, datasource=None):
    objs = yaml.load(yamldata)
    if objs:
        return dictserializer.LoadModel(objs, reqclsname, datasource)
    else:
        return []

def SaveModel(model, data="", objs=None, datasource=None, userfunc=None, greedy=False, class_mapping={}, inst_mapping={}):
    # save children
    if objs == None:
        objs = []
    if model in inst_mapping:
        klassmap = inst_mapping[model]
    elif model.__class__.__name__ in class_mapping:
        klassmap = class_mapping[model.__class__.__name__]
    else:
        klassmap = None
    if not (greedy and (model._datasource or klassmap)) and not model._datasource == datasource and not model == datasource:
        # this node doesn't belong to this datasource.
        return data
    objs.append(model)
    model = model.getSelfToPersist()
    if not isinstance(model,Filter):
        for child in model.getAllReferences():
            if child not in objs:
                data = SaveModel(child, data, objs, datasource, userfunc, greedy, class_mapping, inst_mapping)
    # to dict
    if klassmap:
        props = { "children" : map(lambda s: str(s.uuid),model.getChildrenToPersist()) }
        obj = {str(klassmap)+"#"+str(model.uuid): props}
    else:
        obj = dictserializer.SaveModel(model)
    # dump to yaml
    if userfunc:
        userfunc(yaml.dump(obj))
    else:
        data += yaml.dump(obj)
    return data

