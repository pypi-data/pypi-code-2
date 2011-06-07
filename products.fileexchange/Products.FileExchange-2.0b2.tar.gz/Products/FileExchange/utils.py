from Products.CMFCore.utils import getToolByName

def createFileExchangeContainer(user, event):

    try:
        inst = getToolByName(user, 'portal_quickinstaller');
        if not inst.isProductInstalled('FileExchange'):
            return

        pm = getToolByName(user, 'portal_membership')
        folder = pm.getHomeFolder(id=user.getUserName(), verifyPermission=True)

        if folder is None:
            pm.createMemberArea(member_id=user.getUserName())
            folder = pm.getHomeFolder(id=user.getUserName(), verifyPermission=True)

        typestool = getToolByName(user, 'portal_types')
        typestool.constructContent(type_name="FileExchange Container", container=folder, id="files")
        folder = folder['files']
        folder.edit(title='File exchange')
        folder.reindexObject()
    except:
        pass