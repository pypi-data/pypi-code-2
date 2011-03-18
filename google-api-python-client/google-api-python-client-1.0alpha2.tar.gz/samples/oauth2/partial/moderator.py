#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Moderator.

Command-line application that exercises the Google Moderator API.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import gflags
import httplib2
import logging
import pprint
import sys

from apiclient.discovery import build
from apiclient.model import LoggingJsonModel
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

FLAGS = gflags.FLAGS
FLOW = OAuth2WebServerFlow(
    client_id='433807057907.apps.googleusercontent.com',
    client_secret='jigtZpMApkRxncxikFpR+SFg',
    scope='https://www.googleapis.com/auth/moderator',
    user_agent='moderator-cmdline-sample/1.0')

gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')

DISCOVERY_URI = ('https://www-googleapis-test.sandbox.google.com/discovery/v0.3/describe/'
  '{api}/{apiVersion}')

def main(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  storage = Storage('moderator.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid == True:
    credentials = run(FLOW, storage)

  proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_HTTP, 'cache.corp.google.com', 3128)
  http = httplib2.Http(cache=".cache", proxy_info=proxy_info)
  http = credentials.authorize(http)

  service = build("moderator", "v1", http=http,
      discoveryServiceUrl=DISCOVERY_URI,
      model=LoggingJsonModel())

  series_body = {
      "data": {
        "description": "Share and rank tips for eating healthy and cheap!",
        "name": "Eating Healthy & Cheap",
        "videoSubmissionAllowed": False
        }
      }
  series = service.series().insert(body=series_body).execute()
  print "Created a new series"

  topic_body = {
      "data": {
        "description": "Share your ideas on eating healthy!",
        "name": "Ideas",
        "presenter": "liz"
        }
      }
  topic = service.topics().insert(seriesId=series['id']['seriesId'],
                            body=topic_body).execute()
  print "Created a new topic"

  submission_body = {
      "data": {
        "attachmentUrl": "http://www.youtube.com/watch?v=1a1wyc5Xxpg",
        "attribution": {
          "displayName": "Bashan",
          "location": "Bainbridge Island, WA"
          },
        "text": "Charlie Ayers @ Google"
        }
      }
  full_submission = service.submissions().insert(seriesId=topic['id']['seriesId'],
      topicId=topic['id']['topicId'], body=submission_body).execute()

  print "Inserted a new submisson on the topic"
  pprint.pprint(full_submission)

  submission = service.submissions().get(seriesId=full_submission['id']['seriesId'],
      submissionId=full_submission['id']['submissionId'],
      fields='geo(latitude,longitude),text').execute()

  print "Retrieve just some fields of the submission"
  pprint.pprint(submission)

  vote_body = {
      "data": {
        "vote": "PLUS"
        }
      }
  vote = service.votes().insert(seriesId=full_submission['id']['seriesId'],
                   submissionId=full_submission['id']['submissionId'],
                   body=vote_body).execute()
  print "Voted on the submission"
  pprint.pprint(vote)


  print "Patch the vote."
  vote_body = {
      "data": {
        "vote": "MINUS"
        }
      }

  my_votes = service.votes().list(seriesId=vote['id']['seriesId']).execute()
  pprint.pprint(my_votes)


  new_vote = service.votes().patch(seriesId=vote['id']['seriesId'],
                   submissionId=vote['id']['submissionId'],
                   body=vote_body).execute()
  print "Updated vote on the submission"
  pprint.pprint(vote)

if __name__ == '__main__':
  main(sys.argv)
