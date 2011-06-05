import random, csv

class __Name__(object):
    
    def __init__(self, name, freq=None, cum_freq=None, rank=None):
        self.name = name
        self.freq = freq
        self.cum_freq = cum_freq
        self.rank = rank
        
    def __str__(self):
        return("%s, %f, %f, %d" % (self.name, self.freq, self.cum_freq, self.rank,))
    
    def as_list(self):
        return [self.name, self.freq, self.cum_freq, self.rank]
        
class Names(object):
    ''' Names, based on the list published by the U.S. Census Bureau, Population Division.
        See http://www.census.gov/genealogy/names/names_files.html for details. '''
        
    def __init__(self):
        self.last_names = []
        self.male_names = []
        self.female_names = []
        self.__load_csv__()
        
    def random_fullname(self, gender):
        ''' Returns a name like "John Smith" or "Mary Williams". '''
        if gender in ['M', 'm', 'Male', 'MALE', 'male']:
            first = random.choice(self.male_names).name
        elif gender in ['F', 'f', 'Female', 'FEMALE', 'female']:
            first = random.choice(self.female_names).name
        else:
            raise ValueError('''Please use 'M', 'm', 'Male', 'MALE', 'male', 
                                'F', 'f', 'Female', 'FEMALE', 'female' 
                                for gender argument.''')
        last = random.choice(self.last_names).name
        return ("%s %s" % (first, last))
        
    def random_male_firstname(self):
        ''' Returns a name like "John". '''
        return random.choice(self.male_names).name
        
    def random_female_firstname(self):
        ''' Returns a name like "Mary". '''
        return random.choice(self.female_names).name
        
    def random_lastname(self):
        ''' Returns a name like "Smith". '''
        return random.choice(self.last_names).name
        
    def __dump_csv__(self):
        ''' Writes nanes to csv file. Currently hardcoded paths. '''
        csvfile = csv.writer(open('data/last_names.csv','w'))
        for n in self.last_names:
            csvfile.writerow(n.as_list())
        csvfile = csv.writer(open('data/male_names.csv','w'))
        for n in self.male_names:
            csvfile.writerow(n.as_list())
        csvfile = csv.writer(open('data/female_names.csv','w'))
        for n in self.female_names:
            csvfile.writerow(n.as_list())
        
    def __load_csv__(self):
        ''' Reads nanes from csv file. Currently hardcoded paths. '''
        csvfile = csv.reader(open('data/last_names.csv','r'))
        for row in csvfile:
            [aname, afreq, acum_freq, arank] = row
            self.last_names.append(__Name__(aname.title(), freq=float(afreq),
                                        cum_freq=float(acum_freq),
                                        rank=int(arank)))
        csvfile = csv.reader(open('data/male_names.csv','r'))
        for row in csvfile:
            [aname, afreq, acum_freq, arank] = row
            self.male_names.append(__Name__(aname.title(), freq=float(afreq),
                                        cum_freq=float(acum_freq),
                                        rank=int(arank)))
        csvfile = csv.reader(open('data/female_names.csv','r'))
        for row in csvfile:
            [aname, afreq, acum_freq, arank] = row
            self.female_names.append(__Name__(aname.title(), freq=float(afreq),
                                        cum_freq=float(acum_freq),
                                        rank=int(arank)))
    
