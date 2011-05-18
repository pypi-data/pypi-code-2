import resources

class AnalyticaObject(object):
    """
    A class from Senzafine Analytica service

    Every class extending this one must call super(MySubclass, self).__init__
    upon it's own initialization
    """

    # the associated resources.Resource subclass
    ResourceClass = None

    # the list of simple attributes from resource
    basic_attrs = None

    def __init__(self, resource=None):
        self.resource = resource
        self.id = None

    def reload(self):
        """
        Reload informations about this object
        """
        cls = self.__class__
        resource = cls.ResourceClass.get(self.id)
        self._from_resource(resource)

    def _from_resource(self, resource):
        """
        Fill the AnalyticaObject based on this resource

        This method fills the object with the basic_attrs of the class.
        If you have relations or other specific attributes, re-implement
        this method at subclass, calling this one at the begining
        """
        cls = self.__class__
        for att in list(cls.basic_attrs) + ['id']:
            v = getattr(resource, att)
            setattr(self, att, v)
        self.resource = resource
        return self

    def _to_resource(self):
        """
        Get a connected resource from this object

        If you want to do specific processings before sending
        the resource to server, re-implement this method,
        calling this one at the begining
        """
        res = self.__class__.ResourceClass()
        for att in self.basic_attrs:
            setattr(res, att, getattr(self, att))
        return res

    @classmethod
    def get(cls, id=None):
        result = cls.ResourceClass.get(id)
        if not isinstance(result, list):
            x = cls()
            x._from_resource(result)
            return x
        return [cls()._from_resource(i) for i in result]

    def save(self):
        resource = self._to_resource()
        resource.save()
        self._from_resource(resource)

    def delete(self):
        if not self.resource:
            raise AttributeError('%s object is not bound to a resource' % \
                                    self.__class__.__name__)
        self.resource.delete()
        self.id = None


class ContentImporter(AnalyticaObject):
    ResourceClass = resources.UploadImporter
    basic_attrs = ('name', 'description', 'data')

    def __init__(self, name=None, description=None, data=None):
        super(ContentImporter, self).__init__()
        self.id = None
        self.name = name
        self.description = description
        self.data = data


class Column(object):
    def __init__(self, name=None, datatype=None, translation=None):
        self.name = name
        self.datatype = datatype
        self.translation = translation or {}

    def to_dict(self):
        x = dict()
        x['name'] = self.name
        x['datatype'] = self.datatype
        x['valuetranslation_set'] = []
        for k, v in self.translation.items():
            t = {'original': k, 'translation': v}
            x['valuetranslation_set'].append(t)
        return x


    @classmethod
    def from_dict(cls, data):
        o = cls()
        o.name = data['name']
        o.datatype = data['datatype']
        o.translation = {}
        for x in data['valuetranslation_set']:
            o.translation[x['original']] = x['translation']
        return o


class FileParser(AnalyticaObject):
    ResourceClass = resources.FileParser
    basic_attrs = ('name', 'description', 'formattype', 'table', 'separator',
                    'initial_line', 'ending_line')

    def __init__(self, name=None, description=None, formattype='csv',
                    table='', separator=';', initial_line=0,
                    ending_line=None, columns=None):
        super(FileParser, self).__init__()
        self.name = name
        self.description = description
        self.formattype = formattype
        self.table = table
        self.separator = separator
        self.initial_line = initial_line
        self.ending_line = ending_line
        self.columns = columns

    def _to_resource(self):
        res = super(FileParser, self)._to_resource()

        res.column_set = []
        for c in self.columns:
            res.column_set.append(c.to_dict())
        return res

    def _from_resource(self, resource):
        super(FileParser, self)._from_resource(resource)

        self.columns = []
        cols = resource['column_set']
        for c in cols:
            self.columns.append(Column.from_dict(c))
        return self


class Dataset(AnalyticaObject):
    ResourceClass = resources.Dataset
    basic_attrs = ('name', 'description')

    def __init__(self, name=None, description=None,
                    importer=None, parser=None):
        super(Dataset, self).__init__()
        self.name = name
        self.description = description
        self.importer = importer
        self.parser = parser

    def _to_resource(self):
        res = super(Dataset, self)._to_resource()
        if self.importer is not None:
            if not self.importer.id:
                self.importer.save()
            res.importer = self.importer.id

        if self.parser is not None:
            if not self.parser.id:
                self.parser.save()
            res.parser = self.parser.id
        return res

    def _from_resource(self, resource):
        super(Dataset, self)._from_resource(resource)

        self.importer = ContentImporter.get(resource.importer['id'])
        self.parser = FileParser.get(resource.parser['id'])


class ModelType(AnalyticaObject):
    ResourceClass = resources.ModelType
    basic_attrs = ('name', 'display_name', 'description', 'api_alias')

    def save(self):
        raise AttributeError('You cannot save a model type')

    def delete(self):
        raise AttributeError('You cannot delete a model type')


class Status(AnalyticaObject):
    ResourceClass = resources.Status
    basic_attrs = ('name', 'display_name', 'description', 'api_alias')

    def save(self):
        raise AttributeError('You cannot save a model type')

    def delete(self):
        raise AttributeError('You cannot delete a model type')


class Model(AnalyticaObject):
    ResourceClass = resources.Model
    basic_attrs = ('name', )

    def __init__(self, name=None, description=None,
                    dataset=None, modeltype=None):
        self.name = name
        self.description = description
        self.dataset = dataset
        self.modeltype = modeltype
        self.status = None

    def _from_resource(self, resource):
        super(Model, self)._from_resource(resource)
        self.dataset = Dataset.get(resource.dataset['id'])
        self.modeltype = ModelType.get(resource.model_type['id'])
        self.status = Status.get(resource.status['id'])
        return self

    def _to_resource(self):
        res = super(Model, self)._to_resource()

        if not self.modeltype.id:
            self.modeltype.save()
        if not self.dataset.id:
            self.dataset.save()

        res.model_type = self.modeltype.id
        res.dataset = self.dataset.id
        return res

    def answer(self, pattern):
        if (self.status.id != Status.TRAINED.id):
            raise ValueError('You must wait until the training is finished')
        res = resources.Answer()
        if isinstance(pattern, list):
            pattern = dict(enumerate(pattern))
        return res.get(self.id, pattern)

def connect(email, password):
    def get_status_list():
        for s in Status.get():
            setattr(Status, s.api_alias.upper(), s)

    def get_modeltypes():
        for m in ModelType.get():
            setattr(ModelType, m.api_alias.upper(), m)

    resources.connect(email, password)
    Status.ALL = get_status_list()
    ModelType.ALL = get_modeltypes()
