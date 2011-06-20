from dm.dom.stateful import *
from kforge.ioc import *

registry = RequiredFeature('DomainRegistry')

# Todo: Figure out how to switch repository.
    
def getSvnChoices(tracProject):
    available = []
    if tracProject:
        if 'svn' in registry.plugins:
            plugin = registry.plugins['svn']
            register = plugin.services[tracProject.service.project]
            [available.append(s) for s in register]
        if 'mercurial' in registry.plugins:
            plugin = registry.plugins['mercurial']
            register = plugin.services[tracProject.service.project]
            [available.append(s) for s in register]
        if 'git' in registry.plugins:
            plugin = registry.plugins['git']
            register = plugin.services[tracProject.service.project]
            [available.append(s) for s in register]
        registry.services.sortDomainObjects(available)
    return [(s.id, s.name) for s in available]
        
class TracProject(SimpleDatedObject):
    "Definition of TracProject domain object."

    isUnique = False
    isEnvironmentInitialised = Boolean(isHidden=True)
    service = HasA('Service', comment='A trac service.', isRequired=False)
    svn     = HasA('Service', getChoices=getSvnChoices, title='Subversion repository', comment='A project repository (svn or mercurial service).', isRequired=False)
    path    = String(isHidden=True, default='/', title='Svn path', isRequired=False, comment='A path within the chosen Subversion repository.')

    def getLabelValue(self):
        svnLabelValue = ''
        if self.svn:
            svnLabelValue = self.svn.getLabelValue()
        else:
            svnLabelValue = 'no-subversion-repository'
        if self.service:
            serviceLabelValue = self.service.getLabelValue()
        else:
            serviceLabelValue = 'no-parent-service'
        
        return "%s-%s" % (
            serviceLabelValue,
            svnLabelValue,
        )
            

registry.registerDomainClass(TracProject)

