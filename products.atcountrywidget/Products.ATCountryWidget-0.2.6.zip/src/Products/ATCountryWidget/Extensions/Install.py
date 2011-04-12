# Copyright (c) 2004 gocept. All rights reserved.
# See also LICENSE.txt
# $Id: Install.py 236779 2011-04-01 05:51:02Z nilo $


from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.ATCountryWidget.config import PROJECTNAME, GLOBALS, INSTALL_DEMO_TYPE
import string
import os.path
from OFS import PropertySheets
from StringIO import StringIO
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.ATCountryWidget.CountryTool import CountryUtils


def install(self):
    out = StringIO()

    # install demo type
    if INSTALL_DEMO_TYPE:
        installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)

    # install skin layer containing widget macros    
    install_subskin(self, out, GLOBALS)

    # install country tool
    if not hasattr(self, CountryUtils.id):
        self.manage_addProduct['ATCountryWidget'].manage_addTool('ATCountryWidget_Utilities')

    # add "a few" example countries
    countrytool = getToolByName(self, CountryUtils.id)
    if countrytool.listAreas() == ():
        countrytool.manage_countries_addArea('Europe (Western)')
        countrytool.manage_countries_addCountryToArea('Europe (Western)', ['DK','FI','FR','IT','NL','PT','ES','GB','IS','IE','LI','LU','NO','SE','AT','DE','CH','AD','GI','MT','MC','SM','VA','BE','GL','FO','SJ'])
        countrytool.manage_countries_sortArea('Europe (Western)')
        
        countrytool.manage_countries_addArea('Europe (Central)')
        countrytool.manage_countries_addCountryToArea('Europe (Central)', ['CZ','HU','PL','RO','SK','HR','AL','BG','BA','GR','SI','RS','MK'])
        countrytool.manage_countries_sortArea('Europe (Central)')

        countrytool.manage_countries_addArea('Europe (Eastern)')
        countrytool.manage_countries_addCountryToArea('Europe (Eastern)', ['BY','UA','AZ','EE','LV','LT','RU','AM','GE','MD'])
        countrytool.manage_countries_sortArea('Europe (Eastern)')

        countrytool.manage_countries_addArea('North America')
        countrytool.manage_countries_addCountryToArea('North America', ['CA','MX','PM','US','UM'])
        countrytool.manage_countries_sortArea('North America')

        countrytool.manage_countries_addArea('Central America')
        countrytool.manage_countries_addCountryToArea('Central America', ['BZ','CR','SV','GT','HN','NI','PA'])
        countrytool.manage_countries_sortArea('Central America')

        countrytool.manage_countries_addArea('South America')
        countrytool.manage_countries_addCountryToArea('South America', ['AR','BO','BR','CL','CO','EC','FK','GF','GY','PY','PE','SR','UY','VE','GS'])
        countrytool.manage_countries_sortArea('South America')

        countrytool.manage_countries_addArea('Middle East')
        countrytool.manage_countries_addCountryToArea('Middle East', ['LB','BH','IR','IQ','IL','JO','KW','OM','QA','SA','SY','AE','TR','YE','CY'])
        countrytool.manage_countries_sortArea('Middle East')

        countrytool.manage_countries_addArea('Central Asia')
        countrytool.manage_countries_addCountryToArea('Central Asia', ['KZ','KG','TJ','TM','UZ','IO'])
        countrytool.manage_countries_sortArea('Central Asia')

        countrytool.manage_countries_addArea('South Asia')
        countrytool.manage_countries_addCountryToArea('South Asia', ['AF','BD','BT','IN','MV','NP','LK','PK'])
        countrytool.manage_countries_sortArea('South Asia')

        countrytool.manage_countries_addArea('South East Asia')
        countrytool.manage_countries_addCountryToArea('South East Asia', ['BN','KH','ID','LA','MY','MM','PH','SG','TH','TL','VN'])
        countrytool.manage_countries_sortArea('South East Asia')

        countrytool.manage_countries_addArea('North East Asia')
        countrytool.manage_countries_addCountryToArea('North East Asia', ['CN','HK','JP','KP','KR','MN','TW','MO'])
        countrytool.manage_countries_sortArea('North East Asia')

        countrytool.manage_countries_addArea('Australasia')
        countrytool.manage_countries_addCountryToArea('Australasia', ['AU','NZ','AS','CX','CC','CK','FJ','GU','KI','MH','FM','NR','NC','NU','NF','PW','PG','PN','WS','SB','TK','TO','TV','VU','WF','PF','HM','MP','AQ'])
        countrytool.manage_countries_sortArea('Australasia')

        countrytool.manage_countries_addArea('Caribbean')
        countrytool.manage_countries_addCountryToArea('Caribbean', ['AI','AG','AW','BS','BB','BM','KY','CU','DM','DO','GD','GP','HT','JM','MQ','MS','AN','PR','KN','LC','VC','TT','TC','VG','VI'])
        countrytool.manage_countries_sortArea('Caribbean')

        countrytool.manage_countries_addArea('Africa')
        countrytool.manage_countries_addCountryToArea('Africa', ['DZ','AO','BJ','BW','BV','BF','BI','CM','CV','CF','TD','KM','CD','CG','CI','EG','GQ','ER','ET','TF','GA','GM','GN','GW','KE','LS','LR','LY','MG','MW','ML','MR','MU','YT','MA','MZ','NA','NE','NG','RE','RW','ST','SN','SC','SL','SO','ZA','SD','SZ','TZ','TG','TN','UG','ZM','ZW','GH','DJ','EH','SH'])
        countrytool.manage_countries_sortArea('Africa')


    out.write("Successfully installed %s." % PROJECTNAME)
    return out.getvalue()
