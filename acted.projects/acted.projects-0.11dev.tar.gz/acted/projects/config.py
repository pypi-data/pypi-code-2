# -*- coding: utf-8 -*-

"""Common configuration constants
"""
from Products.Archetypes.public import DisplayList

###########################################################################
## ACTED only change what is between the ######## lines !!!!!
## ivan.price@acted.org   14/6/2010
## 
## After changing this file you need to restart plone !

theYears = range(1995,2015)

theDonors = []
theDonors.append(('Bilateral Cooperations','Bilateral Cooperations'))
theDonors.append(('--- All','All Bilateral Cooperations'))
theDonors.append(('--- Afghanistan','Afghanistan'))
theDonors.append(('------- Afghan Government','Afghan Government'))
theDonors.append(('------- Ministry of Agriculture, Irrigation and Livestock (MAIL)','Ministry of Agriculture, Irrigation and Livestock (MAIL)'))
theDonors.append(('------- Ministry of Social Affairs','Ministry of Social Affairs'))
theDonors.append(('------- Minister of Counter Narcotics','Minister of Counter Narcotics'))
theDonors.append(('------- Other:','Other Afghanistan'))
theDonors.append(('----------- NOR CIMIC','NOR CIMIC'))
theDonors.append(('--- Canada','Canada'))
theDonors.append(('------- CIDA/ACDI','CIDA/ACDI'))
theDonors.append(('------- Embassies','Embassies - Canada'))
theDonors.append(('--- Chad','Chad'))
theDonors.append(('--- Congo Brazzaville','Congo Brazzaville'))
theDonors.append(('--- Denmark','Denmark'))
theDonors.append(('------- DANIDA','DANIDA'))
theDonors.append(('--- DRC','DRC'))
theDonors.append(('--- France','France'))
theDonors.append(('------- CIAA','CIAA'))
theDonors.append(('------- Centre de Crise/DAH','Centre de Crise/DAH'))
theDonors.append(('------- Decentralised Cooperation','Decentralised Cooperation'))
theDonors.append(('----------- Cités Unies France','Cités Unies France'))
theDonors.append(('----------- Ville de Paris','Ville de Paris'))
theDonors.append(('----------- Other:','Other France Decentralised Cooperation'))
theDonors.append(('--------------- Agence de l\'eau Adour-Garonne','Agence de l\'eau Adour-Garonne'))
theDonors.append(('--------------- Communautés de Commune de Kreiz Breiz','Communautés de Communede Kreiz Breiz'))
theDonors.append(('--------------- Commune de Guillers','Communede Guillers'))
theDonors.append(('--------------- Commune de Hanvec','Commune de Hanvec'))
theDonors.append(('--------------- Commune de Saint Briac','Communede Saint Briac'))
theDonors.append(('--------------- Commune d\'Ornex','Commune d\'Ornex'))
theDonors.append(('--------------- Conseil Général des Côtes d\'Armor','Conseil Général des Côtes d\'Armor'))
theDonors.append(('--------------- Conseil Régional de Bretagne','Conseil Régional de Bretagne'))
theDonors.append(('--------------- Ile de France (Région)','Ile de France (Région)'))
theDonors.append(('--------------- Ville de Fougères','Ville de Fougères'))
theDonors.append(('------- Embassies','Embassies - France'))
theDonors.append(('----------- French MFA','French MFA'))
theDonors.append(('------- Other','Other France'))
theDonors.append(('--- Germany','Germany'))
theDonors.append(('------- Embassies','Embassies - Germany'))
theDonors.append(('------- German MFA','German MFA'))
theDonors.append(('------- GTZ','GTZ'))
theDonors.append(('--- Iraq','Iraq'))
theDonors.append(('------- CPA','CPA'))
theDonors.append(('--- Iran','Iran'))
theDonors.append(('------- Embassies','Embassies - Iran'))
theDonors.append(('--- Japan','Japan'))
theDonors.append(('------- Embassies','Embassies - Japan'))
theDonors.append(('------- JICA','JICA'))
theDonors.append(('--- Latvia','Latvia'))
theDonors.append(('--- Netherlands','Netherlands'))
theDonors.append(('------- Embassies','Embassies - Netherlands'))
theDonors.append(('--- Nicaragua','Nicaragua'))
theDonors.append(('--- Norway ','Norway'))
theDonors.append(('------- NORAD','NORAD'))
theDonors.append(('------- Royal Norwegian Embassy (RNE)','Royal Norwegian Embassy (RNE)'))
theDonors.append(('--- Spain','Spain'))
theDonors.append(('------- AECID','AECID'))
theDonors.append(('--- Sweden','Sweden'))
theDonors.append(('------- SIDA','SIDA'))
theDonors.append(('--- Switzerland','Switzerland'))
theDonors.append(('------- SDC/DDC','SDC/DDC'))
theDonors.append(('--- Tajikistan ','Tajikistan'))
theDonors.append(('--- Turkey','Turkey'))
theDonors.append(('--- UK','UK'))
theDonors.append(('------- DFID','DFID'))
theDonors.append(('------- Embassies','Embassies - UK'))
theDonors.append(('--- USA','USA'))
theDonors.append(('------- BPRM','BPRM'))
theDonors.append(('------- Embassies','Embassies - USA'))
theDonors.append(('------- OFDA','OFDA'))
theDonors.append(('------- USAID','USAID'))
theDonors.append(('------- ARD','ARD'))
theDonors.append(('------- Chemonics','Chemonics'))
theDonors.append(('------- International Fertilizer Development Center (IFDC)','International Fertilizer Development Center (IFDC)'))
theDonors.append(('------- UMCOR','UMCOR'))
theDonors.append(('------- Other','Other USA'))
theDonors.append(('--- Other','Other Bilateral Cooperations'))
theDonors.append(('European Commission','European Commission'))
theDonors.append(('--- All','All'))
theDonors.append(('--- ECHO','ECHO'))
theDonors.append(('--- EuropeAid (AidCo)','EuropeAid (AidCo)'))
theDonors.append(('--- Other:','Other European Commission'))
theDonors.append(('------- Euronaid','Euronaid'))
theDonors.append(('------- Task Force','Task Force'))
theDonors.append(('International Organisations','International Organisations'))
theDonors.append(('--- All','All'))
theDonors.append(('--- ADB/BAD','ADB/BAD'))
theDonors.append(('--- ASEAN','ASEAN'))
theDonors.append(('--- EBRD/BERD','EBRD/BERD'))
theDonors.append(('--- Global Fund','Global Fund'))
theDonors.append(('--- IOM / OIM','IOM / OIM'))
theDonors.append(('--- OSCE','OSCE'))
theDonors.append(('------- WB / BM','WB / BM'))
theDonors.append(('----------- MISFA','MISFA'))
theDonors.append(('----------- NSP','NSP'))
theDonors.append(('----------- Other','Other WB/BM'))
theDonors.append(('--- Other','Other International Organisations'))
theDonors.append(('Private Cooperation','Private Cooperation'))
theDonors.append(('--- All','All'))
theDonors.append(('--- ABN-AMRO','ABN-AMRO'))
theDonors.append(('--- Aga Khan Foundation','Aga Khan Foundation'))
theDonors.append(('--- Assistance Foundation','Assistance Foundation'))
theDonors.append(('--- Association Enfants Démunis Kareen Mane (AED)','Association Enfants Démunis Kareen Mane (AED)'))
theDonors.append(('--- CARE','CARE'))
theDonors.append(('--- Caritas','Caritas'))
theDonors.append(('--- Centre d\'Etude et de Coopération Internationale (CECI)','Centre d\'Etude et de Coopération Internationale (CECI)'))
theDonors.append(('--- Chemonics','Chemonics'))
theDonors.append(('--- Cooperative Housing Foundation (CHF)','Cooperative Housing Foundation (CHF)'))
theDonors.append(('--- Children Aid','Children Aid'))
theDonors.append(('--- Christian Aid','Christian Aid'))
theDonors.append(('--- Clinton Foundation','Clinton Foundation'))
theDonors.append(('--- Concern','Concern'))
theDonors.append(('--- Dan Church Aid (DCA)','Dan Church Aid (DCA)'))
theDonors.append(('--- Eurasian Foundation of Central Asia','Eurasian Foundation of Central Asia'))
theDonors.append(('--- Family Health International','Family Health International'))
theDonors.append(('--- Fondation de France','Fondation de France'))
theDonors.append(('--- France Culture','France Culture'))
theDonors.append(('--- GTZ','GTZ'))
theDonors.append(('--- HIVOS','HIVOS'))
theDonors.append(('--- Interchurch Organisation for Development Cooperation (ICCO)','Interchurch Organisation for Development Cooperation (ICCO)'))
theDonors.append(('--- International Rescue Committee (IRC)','International Rescue Committee (IRC)'))
theDonors.append(('--- Musée Guimet','Musée Guimet'))
theDonors.append(('--- Norwegian Church Aid / Norwegian Refugee Council (NCA / NRC)','Norwegian Church Aid / Norwegian Refugee Council (NCA/NRC)'))
theDonors.append(('--- Novib','Novib'))
theDonors.append(('--- People In Need (PIN)','People In Need (PIN)'))
theDonors.append(('--- Red Cross / Croix Rouge / IFRC / FICR','Red Cross / Croix Rouge / IFRC / FICR'))
theDonors.append(('--- Reuters','Reuters'))
theDonors.append(('--- ShelterBox UK','ShelterBox UK'))
theDonors.append(('--- Soros Foundation','Soros Foundation'))
theDonors.append(('--- The Christensen Fund (TCF)','The Christensen Fund (TCF)'))
theDonors.append(('--- United Methodist Committee on Relief (UMCOR)','United Methodist Committeeon Relief (UMCOR)'))
theDonors.append(('--- Voix de l\'Enfant (VDE)','Voix de l\'Enfant (VDE)'))
theDonors.append(('--- Vétérinaires Sans Frontières-Belgium (VSF)','Vétérinaires Sans Frontières-Belgium (VSF)'))
theDonors.append(('--- Warchild','Warchild'))
theDonors.append(('--- Welthungerhilfe (WHH)','Welthungerhilfe (WHH)'))
theDonors.append(('--- Other:','Other Private Cooperation'))
theDonors.append(('------- Abbé Pierre','Abbé Pierre'))
theDonors.append(('------- Aid and Relief (AAR)','Aid and Relief (AAR)'))
theDonors.append(('------- AREVA','AREVA'))
theDonors.append(('------- BMB Mott Mac Donald','BMB Mott Mac Donald'))
theDonors.append(('------- Délégation Archéologique Française en Afghanistan (DAFA)','Délégation Archéologique Françaiseen Afghanistan (DAFA)'))
theDonors.append(('------- Diageo','Diageo'))
theDonors.append(('------- ELF Aquitaine','ELF Aquitaine'))
theDonors.append(('------- ELF Congo','ELF Congo'))
theDonors.append(('------- Emmaüs','Emmaüs'))
theDonors.append(('------- Foundation for Development Cooperation – Singapore (FDC)','Foundation for Development Cooperation – Singapore (FDC)'))
theDonors.append(('------- GOAL','GOAL'))
theDonors.append(('------- Goethe Institute','Goethe Institute'))
theDonors.append(('------- Islamic Relief','Islamic Relief'))
theDonors.append(('------- Lions\' Club','Lions\' Club'))
theDonors.append(('------- PRT Paktia','PRT Paktia'))
theDonors.append(('------- Restorers Without Borders / Restaurateurs Sans Frontières','Restorers Without Borders/Restaurateurs Sans Frontières'))
theDonors.append(('------- Société Protectrice des Animaux et de la Nature (SPANA)','Société Protectrice des Animaux et de la Nature (SPANA)'))
theDonors.append(('------- Sri Lanka Nel Cuore','Sri Lanka Nel Cuore'))
theDonors.append(('------- UzPEC','UzPEC'))
theDonors.append(('United Nations','United Nations'))
theDonors.append(('--- All','All'))
theDonors.append(('--- FAO','FAO'))
theDonors.append(('--- UN Habitat','UN Habitat'))
theDonors.append(('--- UNDP / PNUD','UNDP / PNUD'))
theDonors.append(('--- UNESCO','UNESCO'))
theDonors.append(('--- UNHCR','UNHCR'))
theDonors.append(('--- UNICEF','UNICEF'))
theDonors.append(('--- UNOCHA','UNOCHA'))
theDonors.append(('--- WFP / PAM','WFP / PAM'))
theDonors.append(('--- WHO / OMS','WHO / OMS'))
theDonors.append(('--- Other:','Other United Nations'))
theDonors.append(('------- MINUSTAH','MINUSTAH'))
theDonors.append(('------- MONUC','MONUC'))
theDonors.append(('------- Pooled Fund','Pooled Fund'))
theDonors.append(('------- UNAMA','UNAMA'))
theDonors.append(('------- UNDEF','UNDEF'))
theDonors.append(('------- UNFPA','UNFPA'))
theDonors.append(('------- UNIFEM','UNIFEM'))
theDonors.append(('------- UNMIK','UNMIK'))
theDonors.append(('------- UNRWA','UNRWA'))







theSectors = (
'Culture & Heritage',
'Disaster Risk Reduction & Environment',
'Economic Development',
'Education & Training',
'Emergency',
'Food Security & Livelihood',
'Local Governance',
'Shelter & Infrastructure',
'WASH & Health',
'Other'
)


theCountries = (
'Afghanistan',
'Albania',
'Cambodia',
'Central African Republic',
'Chad',
'Congo Brazzaville',
'Democratic Republic of Congo',
'Europe',
'Ethiopia',
'France',
'Haiti',
'India',
'Indonesia',
'Iraq',
'Jordan',
'Kosovo',
'Kenya',
'Kyrgyzstan',
'Lebanon',
'Macedonia',
'Myanmar',
'Nicaragua',
'Niger',
'Occupied Palestinian Territories',
'Pakistan',
'Republic of Congo',
'Serbia',
'Somalia',
'Sri Lanka',
'Sudan',
'Tajikistan',
'Uganda',
'Uzbekistan',
'Vietnam',
'Zimbabwe'
)



############################################################################

ACTED_DONORS = DisplayList()
for donor in theDonors:
   ACTED_DONORS.add(donor[1],donor[0])

ACTED_COUNTRIES = DisplayList()
for country in theCountries:
   ACTED_COUNTRIES.add(country,country)

ACTED_SECTORS = DisplayList()
for sector in theSectors:
   ACTED_SECTORS.add(sector,sector)

ACTED_YEARS = DisplayList()
for year in theYears:
   ACTED_YEARS.add(year,year)


PROJECTNAME = 'acted.projects'
ADD_PERMISSIONS = {
    'ACTEDProject': 'acted.projects: Add ACTED Project',
    'MyMut': 'acted.projects: Add ACTED Project',
}
