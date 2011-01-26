###
# FCKEditor2 - Update Members wysiwyg_editor property for FCK Editor in portal_membership
# jean-mat @ macadames.com
###

from Products.CMFCore.utils import getToolByName




def updateFckUsers(self):
        out = ''
        mtool = getToolByName(self, 'portal_membership')      
        for memberId in mtool.listMemberIds():
            member = mtool.getMemberById(memberId)
            try :
               if 'FCK' in member.wysiwyg_editor :
                  member.setMemberProperties({'wysiwyg_editor': 'FCKeditor',}) 
            except:
               pass           
            
            out+= memberId + ' : ' + member.wysiwyg_editor + '\n'

        return out
