"""
$Id: __init__.py 32542 2006-10-30 21:20:50Z optilude $
"""

import sys

import root
import docfolder
import downloadablefile
import filelink
import proposal
import proposalfolder
import project
import release
import releasefolder

sys.modules['Products.PloneSoftwareCenter.content.PloneSoftwareCenter'] = root
sys.modules['Products.PloneSoftwareCenter.content.PSCDocumentationFolder'] = docfolder
sys.modules['Products.PloneSoftwareCenter.content.PSCFile'] = downloadablefile
sys.modules['Products.PloneSoftwareCenter.content.PSCFileLink'] = filelink
sys.modules['Products.PloneSoftwareCenter.content.PSCImprovementProposal'] = proposal
sys.modules['Products.PloneSoftwareCenter.content.PSCImprovementProposalFolder'] = proposalfolder
sys.modules['Products.PloneSoftwareCenter.content.PSCProject'] = project
sys.modules['Products.PloneSoftwareCenter.content.PSCRelease'] = release
sys.modules['Products.PloneSoftwareCenter.content.PSCReleaseFolder'] = releasefolder

