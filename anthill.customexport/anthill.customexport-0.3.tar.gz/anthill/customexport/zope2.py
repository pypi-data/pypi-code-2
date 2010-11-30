import sys, os

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner

from zope.interface import implements
from Products.Five.browser import BrowserView

from interfaces import ICustomFolderExport

TTW_VIEWLET_CONF = """
  <browser:viewlet
    name="%s"
    manager="%s"

"""

def shasattr(f, n):
    _o = aq_base(aq_inner(f))
    return hasattr(_o, n)

class CustomFolderExport(BrowserView):
    """ @see: ICustomFolderExport """

    implements(ICustomFolderExport)

    def __call__(self):
        action = self.request.form.get('action')
        if action is not None:
            path = self.request.form.get('path')
            return self.export(path=path)
        return self.index()

    def export(self, path, customfolder=None):
        """ @see: ICustomFolderExport#export """

        message = ''

        # meta_type : [postfix, contents reading method]
        objectsmapping = {
            'Script (Python)': ['.py', 'read'],
            'Page Template':['.pt', 'read'],
            'DTML Method':['.dtml','read'],
            'DTML Document':['.dtml','read'],
            'Controller Page Template':['.cpt', 'read'],
            'Controller Python Script':['.cpy','read'],
            'Image':['', 'data'],
            'Folder':['.props', 'read'],
            'File':['', 'data'],
            'TTW View Template' : ['.upt', 'read']
        }

        if not os.path.exists(path):
            message = 'Could not find directory %s! Please create it before exporting' % path
            return self.request.RESPONSE.redirect(self.context.absolute_url()+'/@@customexport?status_message=%s' % message)

        if customfolder is None:
            cs = self.context
        else: cs = customfolder

        # cache results for pvc if possible
        pvc_registrations = []

        lst = cs.objectValues()
        for o in lst:
            ct = ''
            
            if not objectsmapping.has_key(o.meta_type):
                message += 'Objects of type "%s" are currently not exportable!<br/>' % o.meta_type
                continue
            
            exportname = '%s%s' % (o.getId(), objectsmapping.get(o.meta_type)[0])
            __traceback_info__ = (exportname, objectsmapping.get(o.meta_type)[1])

            readmethod = getattr(o , objectsmapping[o.meta_type][1], None)
            if readmethod:
                if callable(readmethod):
                    if shasattr(readmethod, 'aq_base'):
                        if callable(readmethod.aq_base):
                            ct = readmethod()
                        else:
                            if shasattr(readmethod, 'seek'):
                                ct = readmethod.read()
                            else: ct = readmethod
                    else:
                        if shasattr(readmethod, 'data'):
                            ct = readmethod.data
                        else:
                            ct = readmethod()
                else: ct = readmethod
            
            # special handling for pvc templates
            if o.meta_type == 'TTW View Template':
                pvc = self.context.unrestrictedTraverse('registrations.html')
                if len(pvc_registrations) == 0:
                    for reg in pvc.getTemplateViewRegistrations():
                        for _v_reg  in reg['views']:
                            if _v_reg['customized'] != None:
                                pvc_registrations.append(_v_reg)

                for dtp in pvc_registrations:
                    pname = dtp['customized']
                    if pname == o.getId():
                        # XXX here we should get all information about the
                        # correct registration for this template - this is
                        # no easy task but would make it easy to export templates
                        # from pvc including correct configuration
                        pass

            # special handling for base_properties
            if exportname == 'base_properties.props':
                props = o.propdict()
                for p in props.values():
                    p['value'] = getattr(o.aq_base, p['id'])
                    ct += '%(id)s:%(type)s=%(value)s\n' % p

            # we also need some special handling for
            # controller objects - they need .metadata file
            if objectsmapping.get(o.meta_type)[0] in ['.cpt', '.cpy']:
                formactions = o.listFormActions(False)
                formvalidations = o.listFormValidators(False)

                fdm = open('%s/%s' % (path, exportname+'.metadata'), 'wb')
                fdm.seek(0)

                dg = """[default]\ntitle = %s\n""" % o.getId().replace('_', '')
                fdm.write(dg)
                
                fdm.write('\n[validators]\n')
                formvalidations.reverse()
                for va in formvalidations:
                    stk = 'validators.%s.%s = %s\n' % \
                            (str(va.getContextType()).replace('None', ''), \
                            str(va.getButton()).replace('None',''), \
                            ','.join(va.getValidators()))

                    # remove some blather
                    stk = stk.replace('.. =', ' =')
                    fdm.write(stk)

                fdm.write('\n[actions]\n')
                formactions.reverse()
                for ac in formactions:
                    fdm.write(str(ac).replace('None','')\
                            .replace('=', ' = ')\
                            .replace(o.getId(), 'action')\
                            .replace('.. =', ' =') + '\n')

                fdm.close()

            if not ct and not readmethod:
                if o.meta_type == 'Folder':
                    basedir = os.path.join(path, o.getId())
                    os.mkdir(basedir)
                    message += self.export(basedir, customfolder=o)
                else:
                    raise Exception, 'Could not find data for %s' % o.getId()

            fd = open('%s/%s' % (path, exportname), 'wb')
            fd.seek(0)

            try:
                fd.write(ct)
            except UnicodeEncodeError:
                fd.close()
                
                # use encoded write - we seem to have unicode
                import codecs
                ufd = codecs.open('%s/%s' % (path, exportname), encoding='utf8', mode='w')
                ufd.write(ct)
                ufd.close()

        message += ' Objects exported. After having checked correctness of export you can delete contents of this folder.'
        return self.request.RESPONSE.redirect(cs.absolute_url()+'/@@customexport?status_message=%s' % message)
