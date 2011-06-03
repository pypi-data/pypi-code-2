"""
Handle plone.app.iterate events triggering content rules.
"""

def __init__():

    global checkin_action, aftercheckin_action, beforecheckout_action
    global checkout_action, execute_rules

    # execute_rules(event) runs rules defined for the parent.
    # See also execute(context, event) to run rules defined for the
    # context (is execute() preferable?)
    # Both functions bubble up the acquisition chain. 
    try:
        from plone.app.contentrules.handlers import execute_rules
    except ImportError:
        from Acquisition import aq_inner, aq_parent
        from plone.app.contentrules.handlers import execute, is_portal_factory
        # copied from plone.app.iterate 2.0:
        def execute_rules(event):
            """ When an action is invoked on an object,
            execute rules assigned to its parent.
            Base action executor handler """

            if is_portal_factory(event.object):
                return

            execute(aq_parent(aq_inner(event.object)), event)


    def checkin_action(event):
        """Handle plone.app.iterate.interfaces.ICheckinEvent"""
        execute_rules(event)

    def aftercheckin_action(event):
        """Handle plone.app.iterate.interfaces.IAfterCheckinEvent"""
        execute_rules(event)

    def beforecheckout_action(event):
        """Handle plone.app.iterate.interfaces.IBeforeCheckoutEvent"""
        execute_rules(event)

    def checkout_action(event):
        """Handle plone.app.iterate.interfaces.ICheckoutEvent"""
        execute_rules(event)

__init__()
