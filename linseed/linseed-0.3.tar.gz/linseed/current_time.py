import datetime

class CurrentTime(object):
    def display(self):
        return datetime.datetime.now().strftime('%c')
    
    @staticmethod
    def name():
        return 'linseed_current_time'

    @staticmethod
    def description():
        return 'Current timestamp'
