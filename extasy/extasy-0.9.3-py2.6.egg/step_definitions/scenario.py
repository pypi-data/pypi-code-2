# -*- coding: utf-8 -*-
import extasy
from extasy import *

@Given( 'I run "$title" scenario of "$story" story' )
@When( 'I run "$title" scenario of "$story" story' )
@Then( 'I run "$title" scenario of "$story" story' )
def run( context, title, story ):
    ok = extasy.runner.run_story_scenario( story, scenario = title )
    if not ok:
        raise StepFailure( 'Fail running "%s" scenario of "%s" story' % ( title, story ) )