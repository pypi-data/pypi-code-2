from wdmmg.model import Entity, Classifier


# THIS WHOLE THING IS REALLY HACKISH AND NEEDS TO BE RE-DONE


_ENTITY_COLORS = """01;#CA221D
02;#CA221D
03;#CA221D
04;#CA221D
05;#C22769
06;#3F93E1
07;#481B79
08;#6AAC32
09;#42928F
10;#D32645
11;#CD531C
12;#EDC92D
14;#A5B425
15;#211D79
16;#449256
17;#7A2077
19;#CA221D
20;#CA221D
23;#E29826
30;#44913D
32;#2458A3
33;#2458A3
60;#14388C
budget;#333333"""

ENTITY_COLORS = [line.split(';') for line in _ENTITY_COLORS.split('\n')]

COLORS = ['#CA221D', '#CA221D', '#CA221D', '#CA221D', '#C22769', '#3F93E1',
          '#481B79', '#6AAC32', '#42928F', '#D32645', '#CD531C', '#EDC92D',
          '#A5B425', '#211D79', '#449256', '#7A2077', '#CA221D', '#CA221D',
          '#E29826', '#44913D', '#2458A3', '#2458A3', '#14388C']
          
def color_items():
    from wdmmg.lib.color import color_range
    for (name, color) in ENTITY_COLORS:
        print name, color
        Entity.c.update({'name': name},
                         {'$set': {'color': color}})
        classifiers =  Classifier.find({'taxonomy': 'bund',
                                        'name': "/" + name + "../i",
                                        'parent': None})
        classifiers = list(classifiers)
        for i, color in enumerate(color_range(color, len(classifiers))):
            Classifier.c.update({'_id': classifiers[i].id},
                                 {'$set': {'color': color, 'root_color': color}})
    
    for taxonomy in ['gpl', 'fkp']:
        classifiers =  Classifier.find({'taxonomy': taxonomy,
                                        'parent': None})
        for i, classifier in enumerate(classifiers):
            Classifier.c.update({'_id': classifier.id},
                                 {'$set': {'color': COLORS[i], 'root_color': COLORS[i]}})
    