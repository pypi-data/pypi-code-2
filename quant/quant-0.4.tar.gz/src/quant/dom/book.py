from quant.dom.base import SimpleObject, String, HasMany, AggregatesMany, HasA

class Book(SimpleObject):

    isUnique = False

    title = String()
    model = HasA('Model')
    results = AggregatesMany('Result', key='id')
    europeans = HasMany('European', key='id')
    americans = HasMany('American', key='id')

    def getLabelValue(self):
        return self.title or self.id

    def getContracts(self):
        return list(self.europeans) + list(self.americans)

    def countContracts(self):
        return len(self.europeans) + len(self.americans)

    def delete(self):
        for contract in self.getContracts():
            contract.book = None
            contract.save()
        super(Book, self).delete()

