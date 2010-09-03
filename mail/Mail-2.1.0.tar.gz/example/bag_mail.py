import sys
from pipestack.app import App, pipe
from pipestack.ensure import ensure

class TestApp(App):
    pipes = [
        pipe('mail', 'mail.service:MailPipe'),
    ]

@ensure('mail')
def run(bag):
    email_address = raw_input('Please enter a destination email address: ')
    bag.mail.send( 
        'Hello world!',
        to=[email_address],
        from_email='james@example.org',
        from_name='James Gardner',
        subject='Test email',
    )
    print "Mail sent successfully"

app = TestApp()
app.parse_config(sys.argv[1])
app.start_flow(
    run=run,
)
