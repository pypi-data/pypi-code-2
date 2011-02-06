class AbstractResults(object): pass

class BookResults(AbstractResults):

    def __init__(self):
        self.name = None
        self.value = 0
        self.contracts = []
        self.lines = []
        self.greeks = {}


class ContractResults(AbstractResults):

    def __init__(self):
        self.name = None
        self.value = 0
        self.underlyings = []


class UnderlyingResults(AbstractResults):

    def __init__(self):
        self.name = None
        self.value = 0
        self.deliveryPeriods = []


class DeliveryPeriodResults(AbstractResults):

    def __init__(self):
        self.name = None
        self.value = 0
        self.error = 0
        self.delta = 1
        self.gamma = 0
        self.vega = 0



