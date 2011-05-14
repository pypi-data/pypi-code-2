"""Common configuration constants
"""

PROJECTNAME = 'ploneorg.kudobounty'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'BountyProgramSubmission': 'ploneorg.kudobounty: Add Bounty Program Submission',
}

CONTAINER_ID = "bounty-submissions"
CONTAINER_TITLE = "Bounty submissions"

FORM_ID = "bounty-submissions-form"
FORM_PATH = "/".join([CONTAINER_ID, FORM_ID])
TOPIC_ID = "aggregator"
TOPIC_PATH = "/".join([CONTAINER_ID, TOPIC_ID])
