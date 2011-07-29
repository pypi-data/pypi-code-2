# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from redturtle.subsites.frontend.viewlets.logo import LogoViewlet as BaseLogoViewlet

class LogoViewlet(BaseLogoViewlet):
    index = ViewPageTemplateFile('logo.pt')

