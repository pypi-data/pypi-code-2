from quant.django.apps.eui.views.base import QuantView
from dm.view.registry import RegistryNavigation
from dm.view.registry import RegistryFieldNames
from dm.view.registry import RegistryContextSetter
from dm.view.registry import RegistryView
from dm.view.registry import RegistryListView
from dm.view.registry import RegistryCreateView
from dm.view.registry import RegistryReadView
from dm.view.registry import RegistrySearchView
from dm.view.registry import RegistryFindView
from dm.view.registry import RegistryUpdateView
from dm.view.registry import RegistryDeleteView

class SymbolNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/symbols/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/symbols/'}
        )
        items.append(
            {'title': 'New', 'url': '/symbols/create/'}
        )
        return items


class ModelNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/models/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/models/'}
        )
        items.append(
            {'title': 'New', 'url': '/models/create/'}
        )
        return items


class ImageNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/images/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/images/'}
        )
        items.append(
            {'title': 'New', 'url': '/images/create/'}
        )
        return items


class DeliveryPeriodNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/deliveryPeriods/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/deliveryPeriods/'}
        )
        items.append(
            {'title': 'New', 'url': '/deliveryPeriods/create/'}
        )
        return items


class EuropeanNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/europeans/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/europeans/'}
        )
        items.append(
            {'title': 'New', 'url': '/europeans/create/'}
        )
        return items


class AmericanNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/americans/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/americans/'}
        )
        items.append(
            {'title': 'New', 'url': '/americans/create/'}
        )
        return items


class PricerNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/pricers/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/pricers/'}
        )
        items.append(
            {'title': 'New', 'url': '/pricers/create/'}
        )
        return items


class BookNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/books/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/books/'}
        )
        items.append(
            {'title': 'New', 'url': '/books/create/'}
        )
        return items


class ResultNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/results/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/results/'}
        )
        items.append(
            {'title': 'New', 'url': '/results/create/'}
        )
        return items


class QuantRegistryView(RegistryView, QuantView):

    domainClassName = ''
    manipulatedFieldNames = {
    }
    manipulators = {
    }
    redirectors = {
    }
    navigation = {
        'symbols/list':   SymbolNavigation,
        'symbols/create': SymbolNavigation,
        'symbols/read':   SymbolNavigation,
        'symbols/update': SymbolNavigation,
        'symbols/delete': SymbolNavigation,
        'models/list':   ModelNavigation,
        'models/create': ModelNavigation,
        'models/read':   ModelNavigation,
        'models/update': ModelNavigation,
        'models/delete': ModelNavigation,
        'images/list':   ImageNavigation,
        'images/create': ImageNavigation,
        'images/read':   ImageNavigation,
        'images/update': ImageNavigation,
        'images/delete': ImageNavigation,
        'deliveryPeriods/list':   DeliveryPeriodNavigation,
        'deliveryPeriods/create': DeliveryPeriodNavigation,
        'deliveryPeriods/read':   DeliveryPeriodNavigation,
        'deliveryPeriods/update': DeliveryPeriodNavigation,
        'deliveryPeriods/delete': DeliveryPeriodNavigation,
        'europeans/list':   EuropeanNavigation,
        'europeans/create': EuropeanNavigation,
        'europeans/read':   EuropeanNavigation,
        'europeans/update': EuropeanNavigation,
        'europeans/delete': EuropeanNavigation,
        'americans/list':   AmericanNavigation,
        'americans/create': AmericanNavigation,
        'americans/read':   AmericanNavigation,
        'americans/update': AmericanNavigation,
        'americans/delete': AmericanNavigation,
        'pricers/list':   PricerNavigation,
        'pricers/create': PricerNavigation,
        'pricers/read':   PricerNavigation,
        'pricers/update': PricerNavigation,
        'pricers/delete': PricerNavigation,
        'books/list':   BookNavigation,
        'books/create': BookNavigation,
        'books/read':   BookNavigation,
        'books/update': BookNavigation,
        'books/delete': BookNavigation,
        'results/list':   ResultNavigation,
        'results/create': ResultNavigation,
        'results/read':   ResultNavigation,
        'results/update': ResultNavigation,
        'results/delete': ResultNavigation,
    }
    contextSetters = {
    }


class QuantRegistryListView(QuantRegistryView, RegistryListView):
    pass

class QuantRegistryCreateView(QuantRegistryView, RegistryCreateView):
    pass

class QuantRegistryReadView(QuantRegistryView, RegistryReadView):
    pass

class QuantRegistrySearchView(QuantRegistryView, RegistrySearchView):
    pass

class QuantRegistryFindView(QuantRegistryView, RegistryFindView):
    pass

class QuantRegistryUpdateView(QuantRegistryView, RegistryUpdateView):
    pass

class QuantRegistryDeleteView(QuantRegistryView, RegistryDeleteView):
    pass


def view(request, registryPath, actionName='', actionValue=''):
    pathNames = registryPath.split('/')
    pathLen = len(pathNames)
    if not actionName:
        if pathLen % 2:
            actionName = 'list'
        else:
            actionName = 'read'
    if actionName == 'list':
        viewClass = QuantRegistryListView
    elif actionName == 'create':
        viewClass = QuantRegistryCreateView
    elif actionName == 'read':
        viewClass = QuantRegistryReadView
    elif actionName == 'search':
        viewClass = QuantRegistrySearchView
    elif actionName == 'find':
        viewClass = QuantRegistryFindView
    elif actionName == 'update':
        viewClass = QuantRegistryUpdateView
    elif actionName == 'delete':
        viewClass = QuantRegistryDeleteView
    elif actionName == 'undelete':
        viewClass = QuantRegistryUndeleteView
    elif actionName == 'purge':
        viewClass = QuantRegisryPurgeView
    else:
        raise Exception("No view class for actionName '%s'." % actionName)
    view = viewClass(
        request=request,
        registryPath=registryPath,
        actionName=actionName,
        actionValue=actionValue
    )
    return view.getResponse()

