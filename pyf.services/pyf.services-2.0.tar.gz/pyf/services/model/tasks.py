'''
Created on 20 oct. 2009

@author: schemoul
'''
from pyf.services.model import DeclarativeBase
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, String, Boolean
from sqlalchemy.orm import relation

class TubeTask(DeclarativeBase):
    __tablename__ = "tube_tasks"
    
    id = Column(Integer, primary_key=True)
    display_name = Column(Unicode, nullable=False)
    
    tube_id = Column(Integer, ForeignKey('tubes.id'))
    tube = relation('Tube', backref='tasks')
    
    active = Column(Boolean, nullable=False, default=True)
    
    variant_name = Column(Unicode(50), nullable=True)
    
    # Types :
    # - weekdays
    # - monthdays
    # - interval
    type = Column(String, nullable=False)
    
    # Corresponds to either interval time, or timeonday time
    time = Column(String, nullable=False)
    
    # Corresponds either to week days (1-7) or to monthdays (1-31)
    # separated by a comma ','
    days = Column(String, nullable=True)
    
    def get_hours(self):
        value = map(int, self.time.split(':'))
        assert len(value) == 2, \
                        "There should be two values in time: hours and minutes"
        return tuple(value)
        
    def get_days(self):
        return map(int, self.days.split(','))
    
    def schedule(self):
        from pyf.services.core.tasks import (cancel_if_exists,
                                          schedule_interval_tube_launch,
                                          schedule_weekdays_tube_launch,
                                          schedule_monthdays_tube_launch)
        cancel_if_exists(self.id)
        if not self.active:
            raise ValueError, "You can't schedule an inactive task"
        
        if not self.tube_id:
            raise ValueError, "You can't schedule a task without a tube"
        
        if not self.tube.active:
            raise ValueError, "You can't schedule a task with an inactive tube"
        
        if self.tube.needs_source:
            raise ValueError, \
                        "You can't schedule a task with a tube needing a source"
        
        if self.type == 'interval':
            schedule_interval_tube_launch(self.id, self.tube_id,
                                          int(self.time), 
                                          variant=(self.variant_name or None))
        elif self.type == 'weekdays':
            schedule_weekdays_tube_launch(self.id, self.tube_id,
                                          self.get_days(), self.get_hours(),
                                          variant=(self.variant_name or None))
        elif self.type == 'monthdays':
            schedule_monthdays_tube_launch(self.id, self.tube_id,
                                           self.get_days(), self.get_hours(),
                                           variant=(self.variant_name or None))
        else:
            raise ValueError, 'Unknown task type "%s"' % self.type