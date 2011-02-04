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

class MarketNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/markets/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/markets/'}
        )
        items.append(
            {'title': 'New', 'url': '/markets/create/'}
        )
        return items


class EuropeanOptionNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/europeanOptions/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/europeanOptions/'}
        )
        items.append(
            {'title': 'New', 'url': '/europeanOptions/create/'}
        )
        return items


class AmericanOptionNavigation(RegistryNavigation):

    def createMajorItem(self):
        return '/americanOptions/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/americanOptions/'}
        )
        items.append(
            {'title': 'New', 'url': '/americanOptions/create/'}
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


class QuantRegistryView(RegistryView, QuantView):

    domainClassName = ''
    manipulatedFieldNames = {
    }
    manipulators = {
    }
    redirectors = {
    }
    navigation = {
        'markets/list':   MarketNavigation,
        'markets/create': MarketNavigation,
        'markets/read':   MarketNavigation,
        'markets/update': MarketNavigation,
        'markets/delete': MarketNavigation,
        'europeanOptions/list':   EuropeanOptionNavigation,
        'europeanOptions/create': EuropeanOptionNavigation,
        'europeanOptions/read':   EuropeanOptionNavigation,
        'europeanOptions/update': EuropeanOptionNavigation,
        'europeanOptions/delete': EuropeanOptionNavigation,
        'americanOptions/list':   AmericanOptionNavigation,
        'americanOptions/create': AmericanOptionNavigation,
        'americanOptions/read':   AmericanOptionNavigation,
        'americanOptions/update': AmericanOptionNavigation,
        'americanOptions/delete': AmericanOptionNavigation,
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

