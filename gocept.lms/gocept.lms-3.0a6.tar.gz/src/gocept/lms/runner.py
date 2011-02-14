# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lms.check
import gocept.lms.notify
import gocept.lms.schedule
import gocept.lms.sync
import gocept.runner


@gocept.runner.appmain(ticks=60)
def scheduler():
    return gocept.lms.schedule.schedule()


@gocept.runner.appmain(ticks=1)
def checker():
    return gocept.lms.check.check_and_process()


@gocept.runner.appmain(ticks=1)
def notifier():
    return gocept.lms.notify.notify()


@gocept.runner.appmain(ticks=60)
def syncer():
    return gocept.lms.sync.sync()
