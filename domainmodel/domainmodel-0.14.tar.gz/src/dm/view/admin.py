from dm.view.base import *

class AdminView(SessionView):
    
    minorNavigation = [
        {'title': 'Admin',      'url': '/admin/'},
        {'title': 'Model', 'url': '/admin/model/'},
    ]
    majorNavigationItem = '/'
    minorNavigationItem = '/admin/'

    def canAccess(self):
        return self.canUpdateSystem()


class AdminIndexView(AdminView):

    templatePath = 'admin/index'
    

class AdminModelView(AdminView):

    templatePath = 'admin/model'
    minorNavigationItem = '/admin/model/'
    
    def setContext(self):
        super(AdminModelView, self).setContext()
        domainClassRegister = self.registry.getDomainClassRegister()
        domainClassNameList = domainClassRegister.keys()
        domainClassNameList.sort()
        self.context.update({
            'domainClassNameList' : domainClassNameList,
        })


class AdminListView(AbstractListView, AdminView):

    templatePath = 'admin/list'
    minorNavigationItem = '/admin/model/'
        

class AdminCreateView(AbstractCreateView, AdminView):

    templatePath = 'admin/create'
    minorNavigationItem = '/admin/model/'
    
    def makePostManipulateLocation(self):
        return '/admin/model/%s/' % self.domainClassName


class AdminReadView(AbstractReadView, AdminView):

    templatePath = 'admin/read'
    minorNavigationItem = '/admin/model/'


class AdminUpdateView(AbstractUpdateView, AdminView):

    templatePath = 'admin/update'
    minorNavigationItem = '/admin/model/'
    
    def makePostManipulateLocation(self):
        return '/admin/model/%s/%s/' % (
            self.domainClassName, 
            self.domainObject.getRegisterKeyValue(),
        )


class AdminDeleteView(AbstractDeleteView, AdminView):

    templatePath = 'admin/delete'
    minorNavigationItem = '/admin/model/'

    def makePostManipulateLocation(self):
        return '/admin/model/%s/' % self.domainClassName


class AdminListHasManyView(AbstractListHasManyView, AdminView):

    templatePath = 'admin/listHasMany'
    minorNavigationItem = '/admin/model/'


class AdminCreateHasManyView(AbstractCreateHasManyView, AdminView):

    templatePath = 'admin/createHasMany'
    minorNavigationItem = '/admin/model/'

    def makePostManipulateLocation(self):
        return '/admin/model/%s/%s/%s/' % (
            self.domainClassName, self.domainObjectKey, self.hasManyName
        )


class AdminReadHasManyView(AbstractReadHasManyView, AdminView):

    templatePath = 'admin/readHasMany'
    minorNavigationItem = '/admin/model/'


class AdminUpdateHasManyView(AbstractUpdateHasManyView, AdminView):

    templatePath = 'admin/updateHasMany'
    minorNavigationItem = '/admin/model/'

    def makePostManipulateLocation(self):
        return '/admin/model/%s/%s/%s/' % (
            self.domainClassName, self.domainObjectKey, self.hasManyName
        )


class AdminDeleteHasManyView(AbstractDeleteHasManyView, AdminView):

    templatePath = 'admin/deleteHasMany'
    minorNavigationItem = '/admin/model/'

    def makePostManipulateLocation(self):
        return '/admin/model/%s/%s/%s/' % (
            self.domainClassName, self.domainObjectKey, self.hasManyName
        )


def index(request):
    view = AdminIndexView(request=request)
    return view.getResponse()

def model(request):
    view = AdminModelView(request=request)
    return view.getResponse()

def list(request, className):
    view = AdminListView(
        request=request,
        domainClassName=className,
    )
    return view.getResponse()

def create(request, className):
    view = AdminCreateView(
        request=request,
        domainClassName=className,
    )
    return view.getResponse()

def read(request, className, objectKey):
    view = AdminReadView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def update(request, className, objectKey):
    view = AdminUpdateView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def delete(request, className, objectKey):
    view = AdminDeleteView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def listHasMany(request, className, objectKey, hasMany):
    view = AdminListHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
    )
    return view.getResponse()

def createHasMany(request, className, objectKey, hasMany):
    view = AdminCreateHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
    )
    return view.getResponse()

def readHasMany(request, className, objectKey, hasMany, attrKey):
    view = AdminReadHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()

def updateHasMany(request, className, objectKey, hasMany, attrKey):
    view = AdminUpdateHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()

def deleteHasMany(request, className, objectKey, hasMany, attrKey):
    view = AdminDeleteHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()


viewDict = {}
viewDict['ListView']   = AdminListView
viewDict['CreateView'] = AdminCreateView
viewDict['ReadView']   = AdminReadView
viewDict['UpdateView'] = AdminUpdateView
viewDict['DeleteView'] = AdminDeleteView

def view(request, caseName, actionName, className, objectKey):
    if caseName == 'model':
        viewClassName = actionName.capitalize() + 'View'
        viewClass = viewDict[viewClassName]
        viewArgs = []
        if className:
            viewArgs.append(className)
            if objectKey:
                viewArgs.append(objectKey)
        view = viewClass(request=request)
        return view.getResponse(*viewArgs)
    raise Exception, "Case '%s' not supported." % caseName

