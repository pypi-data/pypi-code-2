import os
import shutil
import api
import glob
import database
import turkic.models

def init(args):
    try:
        args[0]
    except IndexError:
        print "Error: Expected argument."
        return

    skeleton = os.path.dirname(__file__) + "/skeleton"
    target = os.getcwd() + "/" + args[0]

    if os.path.exists(target):
        print "{0} already exists".format(target)
        return

    shutil.copytree(skeleton, target);

    for file in glob.glob(target + "/*.pyc"):
        os.remove(file)

    public = os.path.dirname(__file__) + "/public"
    os.symlink(public, target + "/public/turkic")

    print "Initialized new project: {0}".format(args[0]);

def build(args):
    pass

def progress(args):
    print "Balance: ${0:.2f}".format(api.server.balance)

def publish(args):
    session = database.connect()

    try:
        query = session.query(turkic.models.HIT)
        query = query.filter(turkic.models.HIT.published == False)

        for hit in query:
            hit.publish()
            session.add(hit)
            print "Published {0}".format(hit.hitid)

    finally:
        session.commit()
        session.close()

def compensate(args):
    session = database.connect()

    try:
        query = session.query(turkic.models.HIT)
        query = query.filter(turkic.models.HIT.completed == True)
        query = query.filter(turkic.models.HIT.compensated == False)

        for hit in query:
            pass

    finally:
        session.commit()
        session.close()
