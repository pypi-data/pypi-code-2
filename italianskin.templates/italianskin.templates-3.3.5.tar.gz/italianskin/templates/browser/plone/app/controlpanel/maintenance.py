from plone.app.controlpanel.maintenance import MaintenanceControlPanel as CustomMaintenanceControlPanel

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class MaintenanceControlPanel(CustomMaintenanceControlPanel):


    template = ZopeTwoPageTemplateFile('maintenance.pt')
