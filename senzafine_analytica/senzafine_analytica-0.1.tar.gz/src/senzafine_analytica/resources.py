import restful_lib
import urllib
import json


class Connection(restful_lib.Connection):
    URL = 'http://analytica.senzafine.com.br'

    def __init__(self, username, password):
        restful_lib.Connection.__init__(self, Connection.URL, username=username,
                                            password=password)


class Resource(object):
    PATH = '/api'
    CONN = None

    @classmethod
    def get(cls, id=None):
        path = cls.PATH
        if id is not None:
            path += '/' + str(id)

        result = cls.CONN.request_get(path)
        if result['headers']['status'] != '200':
            raise ValueError(result['body'])
        result = json.loads(result['body'])
        if isinstance(result, list):
            retlist = []
            for inst in result:
                i = cls()
                i.__dict__.update(inst)
                retlist.append(i)
            return retlist
        else:
            i = cls()
            i.__dict__.update(result)
            return i

    def __getitem__(self, item):
        return self.__dict__[item]

    def save(self):
        path = self.PATH
        if hasattr(self, 'id') and self.id:
            path += '/' + str(self.id)
        data = {}

        data = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            data[k] = v
        data = json.dumps(data)
        headers = {'Content-Type': 'application/json; charset=UTF-8',
                    'Content-Length': str(len(data)) }

        result = self.CONN.request_put(path, body=data,
                                headers=headers)
        if result['headers']['status'] != '200':
            raise ValueError(result['body'])
        self.__dict__.update(json.loads(result['body']))

    def delete(self):
        path = self.PATH + '/' + str(self.id)
        resp = self.CONN.request_delete(path)
        if resp['headers']['status'] != '200':
            raise ValueError(resp['body'])


class UploadImporter(Resource):
    PATH = '/api/uploadImporters'

    def __init__(self, *args, **kwargs):
        super(UploadImporter, self).__init__(*args, **kwargs)
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        if not isinstance(data, basestring):
            self.content = data.read()
        else:
            self.content = data

class FileParser(Resource):
    PATH = '/api/fileParsers'

class Dataset(Resource):
    PATH = '/api/datasets'

class Status(Resource):
    PATH = '/api/status'

class ModelType(Resource):
    PATH = '/api/modelTypes'

class Model(Resource):
    PATH = '/api/models'

class Answer(Resource):
    PATH = '/api/answer'

    def get(self, model_id, patterns):
        url = self.PATH + '/' + str(model_id)
        urlparms = urllib.urlencode(patterns)
        resp = self.CONN.request_get('%s?%s' % (url, urlparms))
        if resp['headers']['status'] != '200':
            raise ValueError(resp['body'])
        value = json.loads(resp['body'])
        return value['answer']


def connect(username, password):
    con = Connection(username, password)
    resources = [UploadImporter, FileParser, Dataset,
                    Status, ModelType, Model, Answer]
    for resource in resources:
        resource.CONN = con
