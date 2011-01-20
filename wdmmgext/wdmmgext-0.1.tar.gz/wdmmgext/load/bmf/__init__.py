import os
import datapkg

from pylons import config

import plan
from colorize import color_items

def load():
    '''
    Usually access via the Paste Script comment "paster load bmf".
    '''
    
    data_dir = os.path.join(config['getdata_cache'], 'bundeshaushalt')
    
    fkp = file(os.path.join(data_dir, 'funktionenplan_short.csv'), 'r')
    plan.load_file(fkp, taxonomy='fkp')
    fkp.close()
    
    gpl = file(os.path.join(data_dir, 'gruppierungsplan_short.csv'), 'r')
    plan.load_file(gpl, taxonomy='gpl')
    gpl.close()
    
    from load import dataset_from_dir
    for year in [2010]:
    #for year in range(2005, 2011):
        hh_dir = os.path.join(data_dir, 'bundeshaushalt%s' % year)
        dataset_from_dir(hh_dir, year)
        #print hh_dir
    
    color_items()