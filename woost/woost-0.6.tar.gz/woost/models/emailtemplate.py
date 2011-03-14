#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import buffet
import smtplib
from email.mime.text import MIMEText
from email.Header import Header
from email.Utils import formatdate
from cocktail import schema
from cocktail.html.datadisplay import display_factory
from woost.models import Item, Site


class EmailTemplate(Item):

    encoding = "utf-8"

    members_order = [
        "title",
        "mime_type",
        "sender",
        "receivers",
        "bcc",
        "template_engine",
        "subject",
        "body"
    ]

    title = schema.String(
        listed_by_default = False,
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True
    )

    mime_type = schema.String(
        required = True,
        default = "html",
        listed_by_default = False,
        enumeration = [
            "plain",
            "html"
        ],
        text_search = False
    )

    sender = schema.String(
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    receivers = schema.String(
        required = True,
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )
    
    bcc = schema.String(
        listed_by_default = False,
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    template_engine = schema.String(
        enumeration = buffet.available_engines.keys(),
        text_search = False
    )

    subject = schema.String(
        translated = True,
        edit_control = "cocktail.html.TextArea"
    )

    body = schema.String(    
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea"
    )

    def send(self, context = None):

        smtp_host = Site.main.smtp_host or "localhost"
        smtp_port = smtplib.SMTP_PORT
        smtp_user = Site.main.smtp_user
        smtp_password = Site.main.smtp_password

        if context is None:
            context = {}
        
        def eval_member(key):
            expr = self.get(key)
            return eval(expr, context.copy()) if expr else None

        # MIME block
        mime_type = self.mime_type
        pos = mime_type.find("/")

        if pos != -1:
            mime_type = mime_type[pos + 1:]

        # Subject and body (templates)
        if self.template_engine:
            template_engine = buffet.available_engines[self.template_engine]
            engine = template_engine(
                options = {"mako.output_encoding": self.encoding}
            )

            def render(field_name):
                markup = self.get(field_name)
                if markup:
                    template = engine.load_template(
                        "EmailTemplate." + field_name,
                        self.get(field_name)
                    )
                    return engine.render(context, template = template)                    
                else:
                    return u""
           
            subject = render("subject").strip()
            body = render("body")
        else:
            subject = self.subject.encode(self.encoding)
            body = self.body.encode(self.encoding)
            
        message = MIMEText(body, _subtype = mime_type, _charset = self.encoding)

         # Receivers (python expression)
        receivers = eval_member("receivers")
        if receivers:
            receivers = set(r.strip() for r in receivers) 

        if not receivers:
            return set()
 
        message["To"] = ", ".join(receivers)

        # Sender (python expression)
        sender = eval_member("sender")
        if sender:
            message["From"] = sender

        # BCC (python expression)
        bcc = eval_member("bcc")
        if bcc:
            receivers.update(r.strip() for r in bcc)

        if subject:
            message["Subject"] = Header(subject, self.encoding)

        message["Date"] = formatdate()

        # Send the message
        smtp = smtplib.SMTP(smtp_host, smtp_port)
        if smtp_user and smtp_password:
            smtp.login(
                smtp_user.encode(self.encoding), 
                smtp_password.encode(self.encoding)
            )
        smtp.sendmail(sender, list(receivers), message.as_string())
        smtp.quit()

        return receivers

