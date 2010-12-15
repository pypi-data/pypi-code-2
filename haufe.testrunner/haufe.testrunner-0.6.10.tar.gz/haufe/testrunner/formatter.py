##########################################################################
# haufe.testrunner
#
# (C) 2007, 2008, Haufe Mediengruppe
##########################################################################


import os
import socket
import pwd
from datetime import datetime

from styles import styles

now = datetime.now()
now_str = now.strftime('%d.%m.%Y %H:%M:%S')
hostname = socket.gethostname()
ipaddr = socket.gethostbyname(hostname)


def text(results, options, testrunner_id=None, run_id=None):
    """ Write results dict to a text file. 
        Returns the generated report as string.
    """

    fn = os.path.join(options.log_dir, 'report.txt')
    fp = open(fn, 'w')

    print >>fp, 'Testrunner results (%s)' % options.ident
    print >>fp, 'Generated: %s (%s/%s)' % (now_str, hostname, ipaddr)
    print >>fp 
    print >>fp, 'Module                                     Status  Tests OK'
    print >>fp, '-----------------------------------------------------------'

    for k in sorted(results.keys()):

        ok_str = results[k]['tests_ok'] and 'OK' or 'FAILED'
        num_tests = results[k]['number_tests']
        num_failures = results[k]['number_failures']
        num_str = '%s/%s' % (num_tests-num_failures , num_tests)
        print >>fp, '%-40s   %-6s   %s' % (k, ok_str, num_str)

    if testrunner_id and run_id:
        print >>fp
        print >>fp, 'Details: %s/showresults?testrunner_id:int=%d&run_id:int=%d' % (options.base_url, testrunner_id, run_id)
        print >>fp, 'RSS Feed: %s/rss?testrunner_id:int=%d' % (options.base_url, testrunner_id)
    fp.close()

    return open(fn).read()


def html (results, options):
    """ Write results dict to a HTML file. 
        Returns the generated report as string.
    """

    fn = os.path.join(options.log_dir, 'index.html')
    fp = open(fn, 'w')

    print >>fp, '<html><body>'
    print >>fp, '<head>'

    print >>fp, '    <style type="text/css" >'
    print >>fp, styles
    print >>fp, '    </style>'

    print >>fp, '</head>'
    print >>fp, '<body>'
    print >>fp, '<h1>Testrunner results (%s)</h1>' % options.ident
    print >>fp, '<h3>Generated: %s (%s/%s)</h3>' % (now_str, hostname, ipaddr)

    print >>fp, '<table border="1">' 
    print >>fp, '  <thead>' 
    print >>fp, '    <tr>' 
    print >>fp, '      <th>Module</th>' 
    print >>fp, '      <th>Status</th>' 
    print >>fp, '      <th>Tests OK</th>' 
    print >>fp, '    </tr>' 
    print >>fp, '  </thead>' 
    print >>fp, '  <tbody>' 

    for k in sorted(results.keys()):

        ok_str = results[k]['tests_ok'] and 'OK' or 'FAILED'
        num_tests = results[k]['number_tests']
        num_failures = results[k]['number_failures']
        num_str = '%s/%s' % (num_tests-num_failures , num_tests)
        url = '%s/%s' % (options.base_url, results[k]['logfile']) 

        print >>fp, '    <tr class="%s">' % ok_str.upper() 
        print >>fp, '      <td class="MODULE">%s</td>' % k
        print >>fp, '      <td class="%s">%s</td>' % (ok_str.upper(), ok_str)
        print >>fp, '      <td class="COUNTED">%s</td>' % num_str
        print >>fp, '    </tr>' 

    print >>fp, '  </tbody>' 
    print >>fp, '</table>' 

    print >>fp, '</body></html>' 
    print >>fp
    
    fp.close()

    return open(fn).read()

def db(results, options, tests_failed):

    from database.setup import setup
    from database.model import getModel
    from sqlalchemy.orm import sessionmaker

    if options.verbose:
        print 'Connection to %s' % options.dsn

    engine = setup(options.dsn, echo=False)
    Base, mappers = getModel(engine)
    Testrunner, Run, Result = mappers
    Session = sessionmaker(bind=engine)
    session = Session()

    # first we need a testrunner object
    rows = session.query(Testrunner).filter_by(name=unicode(options.ident)).all()

    if rows:
        TR = rows[0]
    else:
        TR = Testrunner(name=unicode(options.ident))
        session.add(TR)

    TR = session.query(Testrunner).filter_by(name=unicode(options.ident)).one()
    TR.last_run = now
    testrunner_id = TR.id

    # now we need a new Run object
    report_file = os.path.join(options.log_root, options.timestamp, 'index.html')
    description = None
    if os.path.exists(report_file):
        description = open(report_file).read()            

    tests_total = tests_passed = 0
    for k in sorted(results.keys()):
        tests_passed += (results[k]['number_tests'] - results[k]['number_failures'])
        tests_total += results[k]['number_tests']

    R = Run(created=datetime.now(),
            link='%s/logs/%s/index.html' % (options.base_url, options.timestamp),
            description=description,
            hostname=socket.gethostname(),
            run_ok=(tests_total==tests_passed),
            results_cumulated='%d/%d' % (tests_passed, tests_total),
            ipaddress=socket.gethostbyname(socket.gethostname()),
            creator=pwd.getpwuid(os.getuid())[00])

    for k in sorted(results.keys()):
        url = '%s/%s' % (options.base_url, results[k]['logfile']) 
        logdata=open(results[k]['logfilepath']).read()
        try:
            logdata = unicode(logdata, 'iso-8859-15', 'ignore').encode('ascii', 'replace')
        except UnicodeError:
            logdata = unicode(logdata, 'utf-8', 'ignore').encode('ascii', 'replace')

        R.result.append(Result(module=unicode(k),
                        tests_passed=results[k]['number_tests'] - results[k]['number_failures'],
                        tests_total=results[k]['number_tests'],
                        tests_ok=results[k]['tests_ok'],
                        logfile=unicode(url),
                        logdata=logdata,
                        ))

    TR.run.append(R)
    session.flush()

    # get hold of the id of the latest run
    run_id = max([run.id for run in TR.run])
    session.commit()
    session.expunge_all()

    # prune runs older than 7 days
    TR = session.query(Testrunner).filter_by(name=unicode(options.ident)).one()
    for run in TR.run:
        if (now - run.created).days  > 7:
            for result in run.result:
                session.delete(result)
            session.delete(run)
    session.flush()
    session.commit()

    return testrunner_id, run_id

