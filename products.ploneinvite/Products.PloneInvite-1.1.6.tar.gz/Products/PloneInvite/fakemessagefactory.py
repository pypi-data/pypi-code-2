class FakeMessageFactory:

    """ Fake MessageFactory, allows calling context.translate() as _(u"") in
    order to be able to use i18ndude on scripts.

    We want to use context.translate(), but if we do, its input strings aren't
    recognized by i18ndude as translatable strings.  If we call it as _(u""),
    i18ndude will recognize it and create translation strings in the .pot file.

    If you have just one script, it's easiest to just define a  '_' method on
    it, but when you have several scripts, you want them all to use the same
    method, which is why we define it here.

    To use in a script:

        from Products.PloneInvite import FakeMessageFactory
        _ = FakeMessageFactory(context,'PloneInvite')

    and

        portalmessage = _(u"Sent invitation to %s.") % invite_to_address

    """

    def __init__(self, context, domain):

        """ The script has the 'context' which supplies the translate() method,
        we also want that in our class. 

        We also set the i18n domain. This will be your product's i18n domain by
        default.
        
        But we can also use default plone translations if we wish, by doing
        this in the script: 

            plonetranslate = FakeMessageFactory(context,'plone')
            message = plonetranslate(u"user")
        """

        self.context = context
        self.domain = domain


    def __call__(self, message):

        """ When called, the class will call the context's translate method on
        the message.
        """

        msgid = message
        return self.context.translate(default=message, domain=self.domain, 
            msgid=msgid)
