import provide.django.settings.main
from dm.view.base import SessionView

class ProvideView(SessionView):

    majorNavigation = []

    def __init__(self, *args, **kwds):
        super(ProvideView, self).__init__(*args, **kwds)
        self._canCreateEarmarkedTime = None
        self._canReadEarmarkedTime = None
        self._canUpdateEarmarkedTime = None
        self._canDeleteEarmarkedTime = None
        self._canCreateScanningSession = None
        self._canReadScanningSession = None
        self._canUpdateScanningSession = None
        self._canDeleteScanningSession = None
        self._canCreateMaintenanceSession = None
        self._canReadMaintenanceSession = None
        self._canUpdateMaintenanceSession = None
        self._canDeleteMaintenanceSession = None
        self._canCreateDowntimeSession = None
        self._canReadDowntimeSession = None
        self._canUpdateDowntimeSession = None
        self._canDeleteDowntimeSession = None
        self._canReadGroup = None
        self._canReadResearcher = None
        self._canReadVolunteer = None
        self._canReadApproval = None
        self._canReadStudy = None
        self._canReadProject = None
        self._canReadTrainingSession = None
        self._canReadReport = None

    def setMajorNavigationItems(self):
        items = []
        if True:
            items.append({'title': 'Schedule',     'url': '/schedule/'})
        if False:
            items.append({'title': 'Contacts',    'url': '/contacts/'})
        if self.canReadGroup():
            items.append({'title': 'Groups',       'url': '/groups/'})
        if self.canReadResearcher():
            items.append({'title': 'Researchers',  'url': '/researchers/'})
        if self.canReadVolunteer():
            items.append({'title': 'Volunteers',   'url': '/volunteers/'})
        if self.canReadApproval():
            items.append({'title': 'Approvals',    'url': '/approvals/'})
        if self.canReadStudy():
            items.append({'title': 'Studies',      'url': '/studies/'})
        if self.canReadProject():
            items.append({'title': 'Projects',     'url': '/projects/'})
        if self.canReadTrainingSession():
            items.append({'title': 'Training',     'url': '/trainingSessions/'})
        if self.canReadReport():
            items.append({'title': 'Reports',      'url': '/reports/'})
        if False:
            items.append({'title': 'My Space',    'url': '/myspace/'})
            items.append({'title': 'Model',       'url': '/admin/model/'})
        if self.canReadSystem():
            items.append({'title': 'Help',         'url': '/help/'})
        self.majorNavigation = items

    def canCreateEarmarkedTime(self):
        if self._canCreateEarmarkedTime == None:
            protectedObject = self.getDomainClass('EarmarkedTime')
            self._canCreateEarmarkedTime = self.canCreate(protectedObject)
        return self._canCreateEarmarkedTime
    
    def canReadEarmarkedTime(self):
        if self._canReadEarmarkedTime == None:
            protectedObject = self.getDomainClass('EarmarkedTime')
            self._canReadEarmarkedTime = self.canRead(protectedObject)
        return self._canReadEarmarkedTime
    
    def canUpdateEarmarkedTime(self):
        if self._canUpdateEarmarkedTime == None:
            protectedObject = self.getDomainClass('EarmarkedTime')
            self._canUpdateEarmarkedTime = self.canUpdate(protectedObject)
        return self._canUpdateEarmarkedTime
    
    def canDeleteEarmarkedTime(self):
        if self._canDeleteEarmarkedTime == None:
            protectedObject = self.getDomainClass('EarmarkedTime')
            self._canDeleteEarmarkedTime = self.canDelete(protectedObject)
        return self._canDeleteEarmarkedTime

    def canCreateScanningSession(self):
        if self._canCreateScanningSession == None:
            protectedObject = self.getDomainClass('ScanningSession')
            self._canCreateScanningSession = self.canCreate(protectedObject)
        return self._canCreateScanningSession

    def canReadScanningSession(self):
        if self._canReadScanningSession == None:
            protectedObject = self.getDomainClass('ScanningSession')
            self._canReadScanningSession = self.canRead(protectedObject)
        return self._canReadScanningSession

    def canUpdateScanningSession(self):
        if self._canUpdateScanningSession == None:
            protectedObject = self.getDomainClass('ScanningSession')
            self._canUpdateScanningSession = self.canUpdate(protectedObject)
        return self._canUpdateScanningSession

    def canDeleteScanningSession(self):
        if self._canDeleteScanningSession == None:
            protectedObject = self.getDomainClass('ScanningSession')
            self._canDeleteScanningSession = self.canDelete(protectedObject)
        return self._canDeleteScanningSession

    def canCreateMaintenanceSession(self):
        if self._canCreateMaintenanceSession == None:
            protectedObject = self.getDomainClass('MaintenanceSession')
            self._canCreateMaintenanceSession = self.canCreate(protectedObject)
        return self._canCreateMaintenanceSession

    def canReadMaintenanceSession(self):
        if self._canReadMaintenanceSession == None:
            protectedObject = self.getDomainClass('MaintenanceSession')
            self._canReadMaintenanceSession = self.canRead(protectedObject)
        return self._canReadMaintenanceSession

    def canUpdateMaintenanceSession(self):
        if self._canUpdateMaintenanceSession == None:
            protectedObject = self.getDomainClass('MaintenanceSession')
            self._canUpdateMaintenanceSession = self.canUpdate(protectedObject)
        return self._canUpdateMaintenanceSession

    def canDeleteMaintenanceSession(self):
        if self._canDeleteMaintenanceSession == None:
            protectedObject = self.getDomainClass('MaintenanceSession')
            self._canDeleteMaintenanceSession = self.canDelete(protectedObject)
        return self._canDeleteMaintenanceSession

    def canCreateDowntimeSession(self):
        if self._canCreateDowntimeSession == None:
            protectedObject = self.getDomainClass('DowntimeSession')
            self._canCreateDowntimeSession = self.canCreate(protectedObject)
        return self._canCreateDowntimeSession
        
    def canReadDowntimeSession(self):
        if self._canReadDowntimeSession == None:
            protectedObject = self.getDomainClass('DowntimeSession')
            self._canReadDowntimeSession = self.canRead(protectedObject)
        return self._canReadDowntimeSession
        
    def canUpdateDowntimeSession(self):
        if self._canUpdateDowntimeSession == None:
            protectedObject = self.getDomainClass('DowntimeSession')
            self._canUpdateDowntimeSession = self.canUpdate(protectedObject)
        return self._canUpdateDowntimeSession
        
    def canDeleteDowntimeSession(self):
        if self._canDeleteDowntimeSession == None:
            protectedObject = self.getDomainClass('DowntimeSession')
            self._canDeleteDowntimeSession = self.canDelete(protectedObject)
        return self._canDeleteDowntimeSession
        
    def canReadGroup(self):
        if self._canReadGroup == None:
            protectedObject = self.getDomainClass('Group')
            self._canReadGroup = self.canRead(protectedObject)
        return self._canReadGroup
        
    def canReadResearcher(self):
        if self._canReadResearcher == None:
            protectedObject = self.getDomainClass('Researcher')
            self._canReadResearcher = self.canRead(protectedObject)
        return self._canReadResearcher
    
    def canReadVolunteer(self):
        if self._canReadVolunteer == None:
            protectedObject = self.getDomainClass('Volunteer')
            self._canReadVolunteer = self.canRead(protectedObject)
        return self._canReadVolunteer
        
    def canReadApproval(self):
        if self._canReadApproval == None:
            protectedObject = self.getDomainClass('Approval')
            self._canReadApproval = self.canRead(protectedObject)
        return self._canReadApproval
        
    def canReadStudy(self):
        if self._canReadStudy == None:
            protectedObject = self.getDomainClass('Study')
            self._canReadStudy = self.canRead(protectedObject)
        return self._canReadStudy
        
    def canReadProject(self):
        if self._canReadProject == None:
            protectedObject = self.getDomainClass('Project')
            self._canReadProject = self.canRead(protectedObject)
        return self._canReadProject
        
    def canReadTrainingSession(self):
        if self._canReadTrainingSession == None:
            protectedObject = self.getDomainClass('TrainingSession')
            self._canReadTrainingSession = self.canRead(protectedObject)
        return self._canReadTrainingSession
        
    def canReadReport(self):
        if self._canReadReport == None:
            protectedObject = self.getDomainClass('Report')
            self._canReadReport = self.canRead(protectedObject)
        return self._canReadReport
        
    def isViewerAdministrator(self):
        if self.session and self.session.person and self.session.person.role:
            if self.session.person.role.name == "Administrator":
                return True
        return False
                                                         
