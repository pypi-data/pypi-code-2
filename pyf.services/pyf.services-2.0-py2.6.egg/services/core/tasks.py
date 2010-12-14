from pyf.services import model
from pyf.services.model import DBSession, Tube, TubeTask
from pyf.services.core.router import Router
from pyf.services.core.events import create_event_track, get_logger

from tgscheduler.scheduler import add_single_task, add_weekday_task,\
    add_monthly_task, add_interval_task, get_task, cancel

import transaction

import logging
logger = logging.getLogger()

def launch_tube(tube_id, user_name=None, variant=None,
                defered=False, options=None, source=None,
                only_prepare=False):
    tube = DBSession.query(Tube).get(tube_id)
    router = Router(tube=tube)
    
    event_track = create_event_track(tube,
                                     variant_name=variant)
    event_track_id = event_track.id
    logger = get_logger(event_track)
    logger.plug_on_event_source(router)
    
    if user_name:
        user = model.User.by_user_name(user_name)
        logger.info(u'Process %s started by user %s with options %s' % (
                        tube.display_name, user.user_name, repr(options)), user=user,
                        source=user.user_name)
    else:
        logger.info(u'Process %s started by scheduler' % tube.display_name,
                    source='scheduler')
    
    transaction.commit()
    
    kwargs = dict(variant=variant,
                  options=options,
                  source=source)
    
    if defered:
        add_single_task(router.process_tube, kw=kwargs,
                        initialdelay=0)
        
        return event_track_id
    
    elif only_prepare:
        return event_track_id, router, kwargs
    
    else:
        return router.process_tube(**kwargs)

def schedule_tasks():    
    tasks = DBSession.query(TubeTask)
    tasks = tasks.join(Tube).filter(Tube.active==True)
    tasks = tasks.filter(Tube.needs_source==False)
    tasks = tasks.filter(Tube.active==True)
    logger.info('Scheduling tasks')
    for task in tasks:
        try:
            logger.info('scheduling task #%d (%s)' % (task.id,
                                                      task.display_name))
            task.schedule()
        except Exception, e:
            logger.exception(e)
    logger.info('Finished scheduling tasks')

def cancel_if_exists(taskname):
    old_task = get_task(taskname)
    if old_task:
        cancel(old_task)
        
def schedule_weekdays_tube_launch(task_id, tube_id,
                                  weekdays, time, variant=None):
    cancel_if_exists(task_id)
    add_weekday_task(launch_tube, weekdays, time,
                     args=[tube_id], kw=dict(variant=variant),
                     taskname=int(task_id))
    logger.info("Task #%s scheduled" % task_id)

def schedule_monthdays_tube_launch(task_id, tube_id,
                                   monthdays, time, variant=None):
    cancel_if_exists(task_id)
    add_monthly_task(launch_tube, monthdays, time,
                      args=[tube_id], kw=dict(variant=variant),
                      taskname=int(task_id))

def schedule_interval_tube_launch(task_id, tube_id,
                                  interval, variant=None):
    cancel_if_exists(task_id)
    add_interval_task(launch_tube, interval=interval,
                      args=[tube_id], kw=dict(variant=variant),
                      initialdelay=interval, taskname=int(task_id))
