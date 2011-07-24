""" Helper function to communicate with a TestSwarm instance
"""
from urllib import quote_plus
import urllib2


def add_testswarm_job(testswarm_url, user, auth, job_name,
                      urls, suites, browsers="popularbeta", max_jobs=1):
    """ Add a job to the TestSwarm instance """
    quoted_urls = "&urls[]=".join(quote_plus(url) for url in [urls])
    quoted_suites = "&suites[]=".join(quote_plus(suite) for suite in [suites])
    job_data = ("state=addjob&output=dump&auth="+auth+
               "&user="+user+"&job_name="+quote_plus(job_name)+
               "&browsers="+browsers+"&urls[]="+quoted_urls+
               "&suites[]="+quoted_suites+"&max="+max_jobs)
    print("Opening %s?%s" %(testswarm_url, job_data))
    usock = urllib2.urlopen(testswarm_url, job_data)
    job_id = usock.read()
    return testswarm_url+job_id

def get_testswarm_job_results(url, job_id):
    """ Collect the results of a TestSwarm job """
    raise NotImplementedError
